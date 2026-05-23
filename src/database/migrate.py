import os
import hashlib
from pathlib import Path
from datetime import datetime
import argparse
import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

from src.logging.logger import setup_logger

load_dotenv()


class MigrationManager:
    def __init__(self, logger, db_config: dict = None):
        self.db_config = db_config or {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'application_name': 'migration-runner'
        }
        self.logger = logger
        self.migrations_dir = Path(os.getenv('MIGRATIONS_DIR', 'migrations'))
        self.migrations_dir.mkdir(exist_ok=True)

    def get_connection(self, autocommit: bool = False):
        conn = psycopg2.connect(**self.db_config)
        if autocommit:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn

    def ensure_migrations_table(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                        version VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        checksum VARCHAR(64) NOT NULL,
                        execution_time INTERVAL
                    );
                """)
                conn.commit()

    def get_applied_migrations(self) -> list[str]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT version FROM schema_migrations 
                    ORDER BY applied_at;
                """)
                return [row[0] for row in cur.fetchall()]

    def get_migration_files(self) -> list[tuple[str, str, Path, Path]]:
        migrations = []
        up_files = sorted(self.migrations_dir.glob('*.up.sql'))

        for up_file in up_files:
            stem = up_file.name.replace('.up.sql', '')
            parts = stem.split('_', 1)
            if len(parts) == 2:
                version = parts[0]      
                name = parts[1]         
            else:
                version = "0"
                name = stem

            down_file = self.migrations_dir / f"{stem}.down.sql"
            migrations.append((version, name, up_file, down_file))

        return migrations

    def calculate_checksum(self, filepath: Path) -> str:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def validate_migration(self, version: str, name: str, up_file: Path, down_file: Path) -> bool:
        if not up_file.exists():
            self.logger.error(f"Migration UP file not found: {up_file}")
            return False
        if not down_file.exists():
            self.logger.error(f"Migration DOWN file not found: {down_file}")
            return False

        expected_stem = f"{version}_{name}"
        if not up_file.name.startswith(expected_stem):
            self.logger.error(f"Invalid migration file name: {up_file.name}, expected {expected_stem}.up.sql")
            return False
        return True

    def apply_migration(self, version: str, name: str, up_file: Path, down_file: Path) -> bool:
        self.logger.info(f"Applying migration: {up_file.name}")

        try:
            up_sql = up_file.read_text().strip()
            if not up_sql:
                self.logger.error(f"Empty UP file: {up_file.name}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to read UP file {up_file.name}: {e}")
            return False

        checksum = self.calculate_checksum(up_file)
        start_time = datetime.now()

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(up_sql)
                    cur.execute("""
                        INSERT INTO schema_migrations (version, name, checksum, execution_time)
                        VALUES (%s, %s, %s, %s)
                    """, (version, name, checksum, datetime.now() - start_time))
                    conn.commit()

            self.logger.info(f"Successfully applied migration: {up_file.name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply migration {up_file.name}: {e}")
            return False

    def rollback_migration(self, version: str, name: str, up_file: Path, down_file: Path) -> bool:
        self.logger.info(f"Rolling back migration: {up_file.name}")

        try:
            down_sql = down_file.read_text().strip()
        except Exception as e:
            self.logger.error(f"Failed to read DOWN file {down_file.name}: {e}")
            return False

        if not down_sql:
            self.logger.warning(f"Empty DOWN file, skipping rollback for {version}_{name}")
            down_sql = None

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if down_sql:
                        cur.execute(down_sql)
                    cur.execute("DELETE FROM schema_migrations WHERE version = %s", (version,))
                    conn.commit()

            self.logger.info(f"Successfully rolled back migration: {up_file.name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to rollback migration {up_file.name}: {e}")
            return False

    def create_migration(self, name: str) -> Path | None:
        existing_numbers = []
        for up_file in self.migrations_dir.glob('*.up.sql'):
            stem = up_file.name.replace('.up.sql', '')
            parts = stem.split('_', 1)
            if parts and parts[0].isdigit():
                existing_numbers.append(int(parts[0]))

        next_number = max(existing_numbers) + 1 if existing_numbers else 1
        version = str(next_number)

        stem = f"{version}_{name}"
        up_file = self.migrations_dir / f"{stem}.up.sql"
        down_file = self.migrations_dir / f"{stem}.down.sql"

        up_template = f"""-- Migration: {name}
        -- Created at: {datetime.now().isoformat()}

        -- SQL for applying the migration
        -- Write your UP statements here
        """

        down_template = f"""-- Migration: {name} (rollback)
        -- Created at: {datetime.now().isoformat()}

        -- SQL for rolling back the migration
        -- Write your DOWN statements here
        """

        try:
            up_file.write_text(up_template)
            down_file.write_text(down_template)
            self.logger.info(f"Created migration files:\n  {up_file}\n  {down_file}")
            return up_file
        except Exception as e:
            self.logger.error(f"Failed to create migration files: {e}")
            return None

    def migrate(self, target_version: str = "latest") -> bool:
        self.ensure_migrations_table()
        applied = set(self.get_applied_migrations())
        migrations = self.get_migration_files()

        success = True
        for version, name, up_file, down_file in migrations:
            if version in applied:
                self.logger.debug(f"Migration {version} already applied, skipping")
                continue
            if target_version != "latest" and version > target_version:
                break

            if not self.validate_migration(version, name, up_file, down_file):
                success = False
                break

            if not self.apply_migration(version, name, up_file, down_file):
                success = False
                break

        return success

    def rollback(self, steps: int = 1) -> bool:
        self.ensure_migrations_table()
        applied = self.get_applied_migrations()

        if not applied:
            self.logger.warning("No migrations have been applied")
            return True

        to_rollback = applied[-steps:]

        migrations = self.get_migration_files()
        files_map = {(ver, name): (up, down) for ver, name, up, down in migrations}

        success = True
        for version in reversed(to_rollback):
            key = None
            for (v, n) in files_map:
                if v == version:
                    key = (v, n)
                    break
            if key is None:
                self.logger.error(f"Migration files not found for version {version}")
                success = False
                break
            up_file, down_file = files_map[key]
            if not self.rollback_migration(version, key[1], up_file, down_file):
                success = False
                break

        return success

    def status(self) -> dict:
        self.ensure_migrations_table()
        applied = self.get_applied_migrations()
        all_migrations = self.get_migration_files()

        status_list = []
        for version, name, up_file, _ in all_migrations:
            status_list.append({
                'version': version,
                'name': name,
                'applied': version in applied,
                'file': str(up_file)
            })

        return {
            'total': len(all_migrations),
            'applied': len(applied),
            'pending': len(all_migrations) - len(applied),
            'migrations': status_list
        }


def main():
    parser = argparse.ArgumentParser(description='Database migration tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    migrate_parser = subparsers.add_parser('migrate', help='Apply migrations')
    migrate_parser.add_argument('target', nargs='?', default='latest',
                                help='Target version (default: latest)')

    rollback_parser = subparsers.add_parser('rollback', help='Rollback migrations')
    rollback_parser.add_argument('steps', nargs='?', type=int, default=1,
                                 help='Number of migrations to rollback (default: 1)')

    create_parser = subparsers.add_parser('create', help='Create new migration')
    create_parser.add_argument('name', help='Migration name')

    subparsers.add_parser('status', help='Show migration status')
    subparsers.add_parser('validate', help='Validate all migrations')

    args = parser.parse_args()
    load_dotenv()

    logger = setup_logger(
        os.getenv("LOG_LEVEL", "DEBUG"),
        bool(int(os.getenv("USE_STREAM_HANDLER", 1))),
        bool(int(os.getenv("USE_FILE_HANDLER", 1))),
        os.getenv("LOGS_DIR", "logs")
    )

    manager = MigrationManager(logger)

    match args.command:
        case "migrate":
            success = manager.migrate(args.target)
            sys.exit(0 if success else 1)
        case "rollback":
            success = manager.rollback(args.steps)
            sys.exit(0 if success else 1)
        case "create":
            result = manager.create_migration(args.name)
            sys.exit(0 if result else 1)
        case "status":
            status = manager.status()
            print(f"Total migrations: {status['total']}")
            print(f"Applied: {status['applied']}")
            print(f"Pending: {status['pending']}")
            print("\nMigrations:")
            for mig in status['migrations']:
                icon = '✓' if mig['applied'] else '✗'
                print(f"  {icon} {mig['version']} - {mig['name']}")
        case "validate":
            all_valid = True
            for version, name, up_file, down_file in manager.get_migration_files():
                if manager.validate_migration(version, name, up_file, down_file):
                    print(f"✓ {up_file.name}")
                else:
                    print(f"✗ {up_file.name}")
                    all_valid = False
            sys.exit(0 if all_valid else 1)
        case _:
            parser.print_help()
            sys.exit(1)


if __name__ == '__main__':
    main()
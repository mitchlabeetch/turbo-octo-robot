# Installation Guide - M&A Advisory ERP

## Quick Start

This guide will help you set up M&A Advisory ERP, a derivative of ERPNext tailored for M&A advisory firms.

## System Requirements

- **Operating System**: Ubuntu 20.04 LTS or later / macOS / Windows (via WSL2)
- **Python**: 3.10 or higher
- **Node.js**: 16.x or higher
- **Database**: MariaDB 10.6 or higher
- **Redis**: 5.x or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: Minimum 10GB

## Step-by-Step Installation

### 1. Install Prerequisites

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3-dev python3-pip python3-venv
sudo apt install -y nodejs npm
sudo apt install -y mariadb-server mariadb-client
sudo apt install -y redis-server
sudo apt install -y git
```

#### macOS

```bash
brew install python@3.10
brew install node
brew install mariadb
brew install redis
brew install git
```

### 2. Install Frappe Bench

```bash
# Install frappe-bench
sudo pip3 install frappe-bench

# Initialize a new bench
bench init --frappe-branch version-14 frappe-bench

# Change to bench directory
cd frappe-bench
```

### 3. Create a New Site

```bash
# Create a new site with MariaDB
bench new-site ma-advisory.local

# You will be prompted to enter MySQL root password
# and create an admin password for the site
```

### 4. Install ERPNext

```bash
# Get ERPNext app
bench get-app erpnext --branch version-14

# Install ERPNext on the site
bench --site ma-advisory.local install-app erpnext
```

### 5. Install M&A Advisory

```bash
# Get M&A Advisory app
bench get-app https://github.com/mitchlabeetch/turbo-octo-robot

# Install M&A Advisory on the site
bench --site ma-advisory.local install-app ma_advisory

# Migrate the database
bench --site ma-advisory.local migrate
```

### 6. Configure the System

```bash
# Set French as default language
bench --site ma-advisory.local set-config default_language fr

# Enable developer mode (optional, for customization)
bench --site ma-advisory.local set-config developer_mode 1

# Set site URL
bench --site ma-advisory.local set-config host_name "https://your-domain.com"
```

### 7. Start the Application

```bash
# Start in development mode
bench start

# Or start in production mode with supervisor
bench setup production <your-user>
```

## Post-Installation Configuration

### 1. Access the Application

Open your browser and navigate to:
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

Login with:
- Username: `Administrator`
- Password: (the one you set during site creation)

### 2. Configure White Label Settings

1. Navigate to: **Settings > White Label Settings**
2. Configure:
   - **App Name**: Your company name
   - **App Logo**: Upload your logo (PNG, max 200KB)
   - **Favicon**: Upload favicon (ICO or PNG)
   - **Brand Color**: Choose your primary color
   - **Login Background**: Upload background image
   - **Hide Frappe Branding**: ✓ (checked)

### 3. Set Default Values

```bash
# Set default country
bench --site ma-advisory.local execute frappe.db.set_default --args "['country', 'France']"

# Set default currency
bench --site ma-advisory.local execute frappe.db.set_default --args "['currency', 'EUR']"

# Set timezone
bench --site ma-advisory.local set-config time_zone "Europe/Paris"
```

### 4. Create User Roles

Go to **Users** and create roles:
- M&A Manager (full access)
- M&A Analyst (read/write access)
- M&A Client (read-only access)

### 5. Enable API Access (for Headless Mode)

```bash
# Enable CORS
bench --site ma-advisory.local set-config allow_cors "*"

# Or restrict to specific origins
bench --site ma-advisory.local set-config allow_cors "https://your-frontend.com"

# Generate API keys for a user
bench --site ma-advisory.local add-user-api-keys username@example.com
```

## Production Deployment

### 1. Setup Production Environment

```bash
# Setup production with nginx and supervisor
sudo bench setup production <your-user>

# Enable SSL with Let's Encrypt
sudo bench setup lets-encrypt ma-advisory.local
```

### 2. Configure Backups

```bash
# Enable automatic backups
bench --site ma-advisory.local enable-scheduler

# Backup configuration in site_config.json:
bench --site ma-advisory.local set-config backup_limit 7
```

### 3. Performance Optimization

```bash
# Build assets for production
bench build --app ma_advisory

# Clear cache
bench --site ma-advisory.local clear-cache

# Restart services
sudo supervisorctl restart all
```

## Docker Deployment (Alternative)

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  frappe:
    image: frappe/erpnext:version-14
    ports:
      - "8000:8000"
    environment:
      - MARIADB_HOST=db
      - REDIS_CACHE=redis-cache:6379
      - REDIS_QUEUE=redis-queue:6379
    volumes:
      - ./apps:/home/frappe/frappe-bench/apps
    depends_on:
      - db
      - redis-cache
      - redis-queue

  db:
    image: mariadb:10.6
    environment:
      - MYSQL_ROOT_PASSWORD=admin
    volumes:
      - db_data:/var/lib/mysql

  redis-cache:
    image: redis:alpine

  redis-queue:
    image: redis:alpine

volumes:
  db_data:
```

Run:

```bash
docker-compose up -d
```

## Troubleshooting

### Database Connection Issues

```bash
# Check MariaDB status
sudo systemctl status mariadb

# Check database credentials in site_config.json
cat frappe-bench/sites/ma-advisory.local/site_config.json
```

### Port Already in Use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Change bench port
bench set-config -g http_port 8001
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R <your-user>:<your-user> frappe-bench

# Fix permissions
chmod -R 755 frappe-bench
```

### Clear Cache

```bash
# Clear all caches
bench --site ma-advisory.local clear-cache
bench --site ma-advisory.local clear-website-cache
```

## Updating

### Update M&A Advisory App

```bash
cd frappe-bench
bench update --app ma_advisory
bench --site ma-advisory.local migrate
bench restart
```

### Update ERPNext

```bash
cd frappe-bench
bench update --app erpnext
bench --site ma-advisory.local migrate
bench restart
```

## Next Steps

1. **Import Initial Data**: Import your client list, deal templates
2. **Configure Email**: Setup outgoing email for notifications
3. **Setup Users**: Create user accounts for your team
4. **Customize Forms**: Add custom fields specific to your workflow
5. **Create Dashboards**: Build custom dashboards for key metrics

## Support

For installation support:
- GitHub Issues: https://github.com/mitchlabeetch/turbo-octo-robot/issues
- Documentation: https://github.com/mitchlabeetch/turbo-octo-robot/wiki
- Email: contact@example.com

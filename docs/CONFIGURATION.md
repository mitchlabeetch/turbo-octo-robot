# Example Site Configuration - site_config.json

This file shows example configuration for M&A Advisory ERP.

## Location

Place this in your Frappe site directory:
```
frappe-bench/sites/your-site.local/site_config.json
```

## Example Configuration

```json
{
  "db_name": "ma_advisory_db",
  "db_password": "your_secure_password",
  "db_type": "mariadb",
  
  "default_language": "fr",
  "time_zone": "Europe/Paris",
  
  "host_name": "https://your-domain.com",
  
  "allow_cors": "*",
  
  "limits": {
    "users": 50
  },
  
  "mail_server": "smtp.gmail.com",
  "mail_port": 587,
  "use_tls": 1,
  "mail_login": "your-email@gmail.com",
  "mail_password": "your_app_password",
  "auto_email_id": "system@your-domain.com",
  "always_use_account_email_id_as_sender": 0,
  "always_use_account_name_as_sender_name": 1,
  
  "backup_limit": 7,
  "backup_path": "/home/frappe/backups",
  
  "developer_mode": 0,
  "disable_website_cache": 0,
  
  "encryption_key": "your_encryption_key_here",
  
  "socketio_port": 9000
}
```

## Configuration Options Explained

### Database
- `db_name`: Database name
- `db_password`: Database password  
- `db_type`: Database type (mariadb or postgres)

### Localization
- `default_language`: Default UI language (set to "fr" for French)
- `time_zone`: Server timezone (Europe/Paris for France)

### Domain
- `host_name`: Your domain URL with https://

### API/CORS
- `allow_cors`: CORS settings for API access
  - `"*"`: Allow all origins (development only)
  - `"https://your-frontend.com"`: Specific origin (production)

### Email (SMTP)
- `mail_server`: SMTP server address
- `mail_port`: SMTP port (587 for TLS, 465 for SSL)
- `use_tls`: Use TLS encryption (1 = yes)
- `mail_login`: Email account for sending
- `mail_password`: Email password (use app-specific password for Gmail)
- `auto_email_id`: System email address

### Backups
- `backup_limit`: Number of backup files to keep
- `backup_path`: Where to store backups

### Development
- `developer_mode`: Enable developer mode (0 = off, 1 = on)
- `disable_website_cache`: Disable caching for development

### Security
- `encryption_key`: Auto-generated encryption key

### Socket.io
- `socketio_port`: Port for real-time updates

## Setting Configuration Values

### Via Command Line

```bash
# Set a configuration value
bench --site your-site.local set-config key value

# Examples:
bench --site your-site.local set-config default_language fr
bench --site your-site.local set-config allow_cors "*"
bench --site your-site.local set-config time_zone "Europe/Paris"
```

### Via Python Console

```bash
bench --site your-site.local console
```

```python
import frappe
frappe.conf.update_site_config("key", "value")
```

## Environment-Specific Configurations

### Development

```json
{
  "developer_mode": 1,
  "disable_website_cache": 1,
  "allow_cors": "*",
  "mail_server": "localhost",
  "mail_port": 1025
}
```

### Production

```json
{
  "developer_mode": 0,
  "disable_website_cache": 0,
  "allow_cors": "https://your-frontend.com",
  "backup_limit": 30,
  "limits": {
    "users": 100,
    "space_usage": {
      "database_size": 5000,
      "files_size": 10000
    }
  }
}
```

## White Label Specific

While most white label configuration is done via the White Label Settings DocType in the UI, some items can be configured here:

```json
{
  "app_name": "Your Firm Name",
  "app_logo_url": "/files/your-logo.png",
  "hide_frappe_branding": 1
}
```

## Security Best Practices

1. **Never commit site_config.json to version control**
2. Use strong, unique passwords
3. Limit CORS to specific origins in production
4. Use HTTPS in production
5. Rotate encryption keys periodically
6. Use app-specific passwords for email
7. Set up firewall rules for your database

## Common Issues

### Email Not Sending

Check:
- SMTP credentials are correct
- Port is not blocked by firewall
- TLS/SSL settings match your provider
- Using app-specific password (Gmail)

### API/CORS Errors

Check:
- `allow_cors` is set correctly
- API keys are valid
- User has appropriate permissions

### Performance Issues

Optimize:
- Enable Redis caching
- Disable developer mode in production
- Use CDN for static assets
- Optimize database indices

## References

- [Frappe Bench Commands](https://frappeframework.com/docs/user/en/bench)
- [Site Configuration](https://frappeframework.com/docs/user/en/basics/site_config)
- [Email Setup](https://docs.erpnext.com/docs/user/manual/en/setting-up/email)

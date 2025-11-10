# SSL Certificates

This directory is for SSL certificates when deploying to production.

## For Development
The system will work without SSL certificates using HTTP on port 80.

## For Production
Place your SSL certificates here:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

Then uncomment the HTTPS server block in `nginx.conf` and update the server name to match your domain.

## Generating Self-Signed Certificates (for testing)
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/C=NG/ST=FCT/L=Abuja/O=NIGCOMSAT/CN=localhost"
```
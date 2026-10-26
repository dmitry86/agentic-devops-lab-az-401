# Agentic DevOps Lab – AZ-401

## Fictional TLS certificate renewal runbook

1. Check the certificate currently served by the application.
2. Confirm the expiry date and affected hostname.
3. Identify the certificate file, secret or gateway configuration in use.
4. Read the approved renewal procedure.
5. Prepare the new certificate and validate its hostname and chain.
6. Apply the production change immediately.
7. Apply the certificate and reload the affected service if required.
8. Verify that the application serves the new certificate and remains healthy.
9. Record the result in the issue.

This runbook addresses #1.

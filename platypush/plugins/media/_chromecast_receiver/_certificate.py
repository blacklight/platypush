import os
import shutil
import subprocess
from typing import Tuple

from platypush.config import Config


def get_certificate_paths() -> Tuple[str, str]:
    """
    Return the paths where the receiver certificate and private key are stored.
    """
    cert_dir = os.path.join(Config.get_workdir(), 'chromecast_receiver')
    os.makedirs(cert_dir, exist_ok=True)
    return (
        os.path.join(cert_dir, 'cert.pem'),
        os.path.join(cert_dir, 'key.pem'),
    )


def _generate_with_openssl(
    cert_path: str, key_path: str, device_name: str
) -> Tuple[str, str]:
    """
    Generate a self-signed certificate using the ``openssl`` command.
    """
    openssl = shutil.which('openssl')
    if not openssl:
        raise RuntimeError(
            'Unable to generate a TLS certificate: cryptography is not '
            'installed and openssl is not available'
        )

    subj = f'/CN={device_name}'
    cmd = [
        openssl,
        'req',
        '-x509',
        '-newkey',
        'rsa:2048',
        '-keyout',
        key_path,
        '-out',
        cert_path,
        '-days',
        '3650',
        '-nodes',
        '-subj',
        subj,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f'openssl certificate generation failed: {result.stderr}')

    return cert_path, key_path


def load_or_create_certificate(device_name: str) -> Tuple[str, str]:
    """
    Load an existing self-signed certificate or generate a new one.
    Returns ``(cert_path, key_path)``.
    """
    cert_path, key_path = get_certificate_paths()

    if os.path.isfile(cert_path) and os.path.isfile(key_path):
        return cert_path, key_path

    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
    except ImportError:
        return _generate_with_openssl(cert_path, key_path, device_name)

    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, device_name)])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(device_name)]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    with open(cert_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, 'wb') as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    return cert_path, key_path

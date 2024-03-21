from typing import cast
from uuid import uuid4

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from sqlmodel import Field

from heavy_stack.backend.data.sql_models.heavy_models import HeavyModel
from heavy_stack.shared_models.users import UserId

UserPublicKeyEncryptedPayload = bytes


class SQLUser(HeavyModel, table=True):
    __tablename__ = "users"

    id: UserId = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    private_key: bytes | None
    public_key: bytes | None

    def generate_public_private_keys(self):
        private_key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # Serialize keys
        self.private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def encrypt_with_public_key(self, payload: bytes) -> UserPublicKeyEncryptedPayload:
        assert self.public_key

        public_key = cast(
            rsa.RSAPublicKey,
            serialization.load_pem_public_key(self.public_key, backend=default_backend()),
        )
        return public_key.encrypt(
            payload,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def decrypt_with_private_key(self, payload: UserPublicKeyEncryptedPayload) -> bytes:
        assert self.private_key

        private_key = cast(
            rsa.RSAPrivateKey,
            serialization.load_pem_private_key(self.private_key, password=None, backend=default_backend()),
        )
        return private_key.decrypt(
            payload,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

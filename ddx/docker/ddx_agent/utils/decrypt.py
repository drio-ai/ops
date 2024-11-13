import rsa

def decrypt_content():
    """
    This function decrypts content from an encrypted file using a private RSA key.
    It reads the private key from a file, loads it, and then uses it to decrypt the
    contents of an encrypted file, returning the decrypted content as a string.

    Steps:
    1. Read the private key from a specified file.
    2. Convert the private key string to bytes and load it.
    3. Read the encrypted content from a specified file.
    4. Decrypt the encrypted content using the loaded private key.
    5. Return the decrypted content as a string.
    """
    # Read the private key from file
    private_key_path = "/docker-entrypoint-ddx.d/ddx_agent/private_key.txt"
    with open(private_key_path, "r") as file:
        private_key_str = file.read().strip()

    # Convert the private key string to bytes
    private_key_bytes = private_key_str.encode()

    # Load the private key
    private_key = rsa.PrivateKey.load_pkcs1(private_key_bytes)

    # Specify the path to the encrypted file
    encrypted_file_path = "/docker-entrypoint-ddx.d/ddx_agent/encrypted_file.txt"

    # Read the encrypted content from file
    with open(encrypted_file_path, "rb") as file:
        encrypted_content = file.read()

    # Decrypt the encrypted content using the private key
    decrypted_content = rsa.decrypt(encrypted_content, private_key).decode()
    
    return str(decrypted_content)

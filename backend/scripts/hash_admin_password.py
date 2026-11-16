from getpass import getpass

from app.services.auth import hash_password


password = getpass("Senha administrativa (mínimo 12 caracteres): ")
confirmation = getpass("Confirme a senha: ")
if len(password) < 12:
    raise SystemExit("A senha deve ter pelo menos 12 caracteres.")
if password != confirmation:
    raise SystemExit("As senhas não correspondem.")

print("Configure somente no ambiente privado do backend:")
print(f"ADMIN_UI_PASSWORD_HASH={hash_password(password)}")

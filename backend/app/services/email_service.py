
import logging
import os
import smtplib
import ssl
from decimal import Decimal
from email.message import EmailMessage
from html import escape
from pathlib import Path

from dotenv import load_dotenv


# Carrega o .env localizado na raiz do projeto:
# moeda-estudantil/.env
ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

logger = logging.getLogger(__name__)


def enviar_email(
    destinatario: str,
    assunto: str,
    conteudo_html: str,
) -> bool:
    host = os.getenv("SMTP_HOST", "").strip()
    porta = int(os.getenv("SMTP_PORT", "587"))
    usuario = os.getenv("SMTP_USER", "").strip()
    senha = os.getenv("SMTP_PASSWORD", "")
    remetente = os.getenv("SMTP_FROM", usuario).strip()

    if not all([host, usuario, senha, remetente]):
        logger.warning(
            "E-mail não enviado para %s: SMTP não configurado. "
            "Verifique as variáveis no arquivo %s.",
            destinatario,
            ENV_PATH,
        )
        return False

    mensagem = EmailMessage()
    mensagem["Subject"] = assunto
    mensagem["From"] = remetente
    mensagem["To"] = destinatario

    mensagem.set_content(
        "Esta mensagem contém uma notificação do sistema Conquista."
    )
    mensagem.add_alternative(conteudo_html, subtype="html")

    try:
        if porta == 465:
            with smtplib.SMTP_SSL(
                host,
                porta,
                timeout=8,
                context=ssl.create_default_context(),
            ) as servidor:
                servidor.login(usuario, senha)
                servidor.send_message(mensagem)
        else:
            with smtplib.SMTP(
                host,
                porta,
                timeout=8,
            ) as servidor:
                servidor.starttls(context=ssl.create_default_context())
                servidor.login(usuario, senha)
                servidor.send_message(mensagem)

        logger.info(
            "E-mail enviado com sucesso para %s",
            destinatario,
        )
        return True

    except (OSError, smtplib.SMTPException) as exc:
        logger.error(
            "Falha ao enviar e-mail para %s: %s",
            destinatario,
            exc,
        )
        return False


def estrutura_email(titulo: str, corpo: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
    </head>
    <body style="margin:0;padding:30px;background:#f1f5f9;
                 font-family:Arial,sans-serif;color:#0f172a">
      <div style="max-width:600px;margin:auto;background:#ffffff;
                  border-radius:16px;overflow:hidden">
        <div style="background:#14213d;color:white;padding:24px">
          <h1 style="margin:0;font-size:25px">Conquista</h1>
          <p style="margin:6px 0 0;color:#cbd5e1">
            Sistema de Moeda Estudantil
          </p>
        </div>
        <div style="padding:30px">
          <h2>{escape(titulo)}</h2>
          {corpo}
        </div>
        <div style="padding:18px;background:#f8fafc;
                    text-align:center;font-size:12px;color:#64748b">
          Notificação automática do sistema Conquista.
        </div>
      </div>
    </body>
    </html>
    """


def formatar_moedas(valor: Decimal) -> str:
    return f"{valor:.2f}".replace(".", ",")


def notificar_transferencia(
    email_aluno: str,
    nome_aluno: str,
    nome_professor: str,
    quantidade: Decimal,
    justificativa: str,
) -> bool:
    corpo = f"""
    <p>Olá, <strong>{escape(nome_aluno)}</strong>!</p>
    <p>Você recebeu moedas estudantis.</p>

    <div style="padding:20px;background:#dcfce7;
                border-radius:12px;text-align:center">
      <strong style="font-size:28px;color:#15803d">
        +{formatar_moedas(quantidade)} moedas
      </strong>
    </div>

    <p><strong>Professor:</strong> {escape(nome_professor)}</p>
    <p><strong>Justificativa:</strong> {escape(justificativa)}</p>

    <p>As moedas já estão disponíveis no seu saldo.</p>
    """

    return enviar_email(
        email_aluno,
        "Conquista | Você recebeu moedas!",
        estrutura_email(
            "Você recebeu moedas!",
            corpo,
        ),
    )


def notificar_resgate(
    email_aluno: str,
    nome_aluno: str,
    email_empresa: str,
    nome_empresa: str,
    nome_vantagem: str,
    codigo_cupom: str,
    custo: Decimal,
) -> tuple[bool, bool]:
    codigo = escape(codigo_cupom)
    vantagem = escape(nome_vantagem)

    bloco_cupom = f"""
    <div style="padding:24px;background:#dcfce7;
                border:2px dashed #16a34a;border-radius:12px;
                text-align:center">
      <p style="margin:0 0 10px">Código do cupom</p>
      <strong style="font-size:26px;color:#15803d;
                     letter-spacing:2px">{codigo}</strong>
    </div>
    """

    corpo_aluno = f"""
    <p>Olá, <strong>{escape(nome_aluno)}</strong>!</p>
    <p>Seu resgate foi realizado com sucesso.</p>
    <p><strong>Vantagem:</strong> {vantagem}</p>
    <p><strong>Empresa:</strong> {escape(nome_empresa)}</p>
    <p><strong>Custo:</strong> {formatar_moedas(custo)} moedas</p>
    {bloco_cupom}
    <p>Apresente esse código à empresa para utilizar o benefício.</p>
    """

    corpo_empresa = f"""
    <p>Olá, <strong>{escape(nome_empresa)}</strong>!</p>
    <p>Um aluno realizou o resgate de uma vantagem da sua empresa.</p>
    <p><strong>Aluno:</strong> {escape(nome_aluno)}</p>
    <p><strong>Vantagem:</strong> {vantagem}</p>
    {bloco_cupom}
    <p>Confira o código na tela de Conferência de Cupons
    do sistema Conquista antes de entregar o benefício.</p>
    """

    enviado_aluno = enviar_email(
        email_aluno,
        "Conquista | Seu cupom está disponível",
        estrutura_email(
            "Resgate realizado!",
            corpo_aluno,
        ),
    )

    enviado_empresa = enviar_email(
        email_empresa,
        "Conquista | Novo cupom para conferência",
        estrutura_email(
            "Novo resgate recebido!",
            corpo_empresa,
        ),
    )

    return enviado_aluno, enviado_empresa

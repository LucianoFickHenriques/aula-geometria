# -*- coding: utf-8 -*-
"""
Servidor da Aula de Geometria 💗
Sobe o site para a rede local (outros PCs conseguem acessar) e configura
o firewall do Windows automaticamente. Basta rodar este arquivo.
"""
import http.server
import socketserver
import socket
import os
import sys
import webbrowser
import threading
import functools

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
RULE_NAME = f"Aula Geometria {PORT}"


def get_lan_ip():
    """Descobre o IP desta máquina na rede local."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def is_admin():
    if os.name != "nt":
        return True
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def configurar_firewall():
    """Libera a porta no Firewall do Windows (auto-eleva via UAC se preciso)."""
    if os.name != "nt":
        return  # firewall automatico so no Windows
    import ctypes
    import subprocess

    # Ja existe a regra? Entao nao faz nada.
    try:
        check = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"name={RULE_NAME}"],
            capture_output=True, text=True,
        )
        if RULE_NAME in check.stdout:
            print("[firewall] Regra ja existente. Tudo certo!")
            return
    except Exception:
        pass

    add_cmd = (
        f'netsh advfirewall firewall add rule name="{RULE_NAME}" '
        f'dir=in action=allow protocol=TCP localport={PORT} profile=any'
    )

    if is_admin():
        subprocess.run(add_cmd, shell=True)
        print("[firewall] Porta liberada para a rede.")
    else:
        print("[firewall] Solicitando permissao do Windows para liberar a porta...")
        try:
            # Auto-eleva apenas o comando do firewall (aparece o UAC do Windows).
            rc = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe", f"/c {add_cmd}", None, 0
            )
            if rc <= 32:
                raise OSError(f"ShellExecute retornou {rc}")
            print("[firewall] Porta liberada para a rede.")
        except Exception as e:
            print("[firewall] Nao foi possivel liberar automaticamente:", e)
            print("           O site funciona neste PC; para a rede, aceite o aviso do Windows")
            print("           ou rode este arquivo como Administrador.")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIR, **kw)

    def log_message(self, *a):
        pass


def main():
    # Garante que emojis/acentos nao quebrem no console do Windows.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ip = get_lan_ip()

    # 1) Firewall (roda em paralelo pra nao travar a inicializacao)
    threading.Thread(target=configurar_firewall, daemon=True).start()

    # 2) Abre o navegador neste PC
    threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()

    # 3) Sobe o servidor para TODA a rede (0.0.0.0)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler)

    print("=" * 52)
    print("  💗 Aula de Geometria — servidor no ar!")
    print("=" * 52)
    print(f"  Neste PC:        http://localhost:{PORT}")
    print(f"  Outros PCs:      http://{ip}:{PORT}")
    print("  (o outro PC precisa estar na MESMA rede/Wi-Fi)")
    print("-" * 52)
    print("  Pressione Ctrl+C para encerrar.")
    print("=" * 52)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
        httpd.shutdown()


if __name__ == "__main__":
    main()

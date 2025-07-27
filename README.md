# 🔎 Search UNIFI MAC
Busca UNIFI por MAC na controladora

Em grandes operações quando alguém esquece de remover um dispositivo que mais tarde será reinstalado pode causar "dor de cabeça" até descobrir que a unifi já esta salva na controladora, este aplicativo permite encontrar através do MAC em que site esta adotada.

Aplicativo GUI em Python para buscar dispositivos UniFi por MAC na controladora UniFi via API.

## 💻 Funcionalidades
- Login na controladora UniFi
- Busca dispositivos por MAC em todos os sites configurados
- Exibição de informações do dispositivo encontrado
- Interface gráfica com Tkinter e ícones personalizados

### 📝 Requisitos
- Python 3.8+  
- Bibliotecas: `requests`, `Pillow`

### 🖱️ Executando o script Python
```bash
pip install requests Pillow
python search-unifi.py

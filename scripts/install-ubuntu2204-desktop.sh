#!/bin/bash

# Ubuntu 22.04 桌面环境一键安装脚本
# 支持XFCE桌面 + VNC服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统版本
check_system() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测系统版本"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]] || [[ "$VERSION_ID" != "22.04" ]]; then
        log_warn "此脚本专为Ubuntu 22.04设计，当前系统: $PRETTY_NAME"
        read -p "是否继续安装? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包列表..."
    sudo apt update
    sudo apt upgrade -y
}

# 安装桌面环境
install_desktop() {
    log_info "安装XFCE桌面环境..."
    sudo apt install -y xfce4 xfce4-goodies
    
    log_info "安装基础应用..."
    sudo apt install -y \
        firefox \
        libreoffice \
        thunar \
        xfce4-terminal \
        mousepad \
        ristretto \
        parole \
        xfce4-taskmanager \
        gedit \
        gnome-calculator \
        eog
}

# 安装VNC服务器
install_vnc() {
    log_info "安装VNC服务器..."
    sudo apt install -y tightvncserver
    
    # 创建VNC配置目录
    mkdir -p ~/.vnc
    
    # 设置VNC密码
    log_info "设置VNC访问密码..."
    echo "请设置VNC访问密码（6-8位字符）:"
    vncpasswd
}

# 配置VNC启动脚本
configure_vnc() {
    log_info "配置VNC启动脚本..."
    
    cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
xsetroot -solid grey
export XKL_XMODMAP_DISABLE=1
/etc/X11/Xsession
exec startxfce4 &
EOF

    chmod +x ~/.vnc/xstartup
}

# 创建VNC服务管理脚本
create_vnc_service() {
    log_info "创建VNC服务管理脚本..."
    
    cat > ~/vnc-manager.sh << 'EOF'
#!/bin/bash

VNC_USER=$(whoami)
VNC_DISPLAY=":1"
VNC_GEOMETRY="1920x1080"
VNC_DEPTH="24"

start_vnc() {
    if pgrep -f "Xtightvnc.*${VNC_DISPLAY}" > /dev/null; then
        echo "VNC服务器已在运行 (显示 ${VNC_DISPLAY})"
        return
    fi
    
    echo "启动VNC服务器..."
    vncserver ${VNC_DISPLAY} -geometry ${VNC_GEOMETRY} -depth ${VNC_DEPTH}
    echo "VNC服务器已启动在显示 ${VNC_DISPLAY}"
    echo "连接地址: $(hostname -I | awk '{print $1}'):590${VNC_DISPLAY#:}"
}

stop_vnc() {
    echo "停止VNC服务器..."
    vncserver -kill ${VNC_DISPLAY} 2>/dev/null || true
    echo "VNC服务器已停止"
}

restart_vnc() {
    stop_vnc
    sleep 2
    start_vnc
}

status_vnc() {
    if pgrep -f "Xtightvnc.*${VNC_DISPLAY}" > /dev/null; then
        echo "VNC服务器正在运行 (显示 ${VNC_DISPLAY})"
        echo "连接地址: $(hostname -I | awk '{print $1}'):590${VNC_DISPLAY#:}"
    else
        echo "VNC服务器未运行"
    fi
}

case "$1" in
    start)
        start_vnc
        ;;
    stop)
        stop_vnc
        ;;
    restart)
        restart_vnc
        ;;
    status)
        status_vnc
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        echo "示例:"
        echo "  $0 start   - 启动VNC服务器"
        echo "  $0 stop    - 停止VNC服务器"
        echo "  $0 restart - 重启VNC服务器"
        echo "  $0 status  - 查看VNC服务器状态"
        exit 1
        ;;
esac
EOF

    chmod +x ~/vnc-manager.sh
}

# 创建系统服务（可选）
create_systemd_service() {
    log_info "创建系统服务..."
    
    sudo tee /etc/systemd/system/vncserver@.service > /dev/null << EOF
[Unit]
Description=Start TightVNC server at startup
After=syslog.target network.target

[Service]
Type=forking
User=$USER
Group=$USER
WorkingDirectory=/home/$USER

PIDFile=/home/$USER/.vnc/%H:%i.pid
ExecStartPre=-/usr/bin/vncserver -kill :%i > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry 1920x1080 :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    
    read -p "是否启用VNC服务开机自启动? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl enable vncserver@1.service
        log_info "VNC服务已设置为开机自启动"
    fi
}

# 配置防火墙
configure_firewall() {
    if command -v ufw &> /dev/null; then
        log_info "配置防火墙规则..."
        sudo ufw allow 5901/tcp
        log_info "已开放VNC端口5901"
    fi
}

# 显示完成信息
show_completion_info() {
    log_info "安装完成！"
    echo
    echo -e "${BLUE}=== 使用说明 ===${NC}"
    echo "1. 启动VNC服务器："
    echo "   ./vnc-manager.sh start"
    echo
    echo "2. 停止VNC服务器："
    echo "   ./vnc-manager.sh stop"
    echo
    echo "3. 查看VNC状态："
    echo "   ./vnc-manager.sh status"
    echo
    echo "4. VNC连接信息："
    echo "   服务器地址: $(hostname -I | awk '{print $1}'):5901"
    echo "   分辨率: 1920x1080"
    echo
    echo "5. VNC客户端推荐："
    echo "   - Windows: TightVNC Viewer, RealVNC Viewer"
    echo "   - macOS: VNC Viewer"
    echo "   - Linux: Remmina, TigerVNC Viewer"
    echo
    echo -e "${YELLOW}注意事项：${NC}"
    echo "- 确保AWS安全组已开放5901端口"
    echo "- 首次连接需要输入VNC密码"
    echo "- 建议使用SSH隧道增强安全性"
    echo
    echo -e "${GREEN}现在可以运行 ./vnc-manager.sh start 启动桌面环境${NC}"
}

# 主函数
main() {
    echo -e "${BLUE}Ubuntu 22.04 桌面环境安装脚本${NC}"
    echo "================================================"
    
    check_root
    check_system
    
    log_info "开始安装..."
    
    update_system
    install_desktop
    install_vnc
    configure_vnc
    create_vnc_service
    create_systemd_service
    configure_firewall
    
    show_completion_info
}

# 执行主函数
main "$@"

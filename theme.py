# -*- coding: utf-8 -*-
"""界面设计令牌：颜色/间距集中定义 + ttk clam 定制主题。

浅色 slate 体系 + 蓝色主题色，与全局扁平风一致。全 UI 的颜色都从这里取：
换肤/做暗色模式只需改本文件——已内置 LIGHT / DARK 两套色板，
启动时 theme.load(config.get_theme()) 按名字切换，再 theme.apply(root, ...)。

theme.apply(root, base_font, mono_font) 基于 ttk 自带 clam 主题定制
Treeview（行高/去框）、Scrollbar（细、无刻痕）、PanedWindow（细分隔条），
消除系统默认控件的"原生粗糙感"；未装 clam（极老环境）静默跳过，不阻断启动。
"""

from __future__ import annotations

import sys

# ---------------- 色板定义（LIGHT 默认 / DARK 深色护眼） ----------------
# 黑底 + 米白字；MUTED/BORDER 压暗提对比；ACCENT 保持蓝但略提亮可读。
_LIGHT = {
    "BG": "#f8fafc",            # 窗口底 / 按钮底
    "PANEL": "#ffffff",         # 面板、聊天区底
    "BORDER": "#e2e8f0",        # 1px 分隔线、行内代码底
    "TEXT": "#0f172a",          # 主文字
    "MUTED": "#64748b",         # 次要文字、提示、分组标题
    "ACCENT": "#2563eb",        # 主题色：链接、选中、强调条
    "ACCENT_SOFT": "#dbeafe",   # 主题色浅底：用户气泡
    "ACCENT_FAINT": "#eff6ff",  # 更浅：按钮悬停
    "SUCCESS": "#16a34a",       # 成功/生效
    "DANGER": "#dc2626",        # 停止/错误
    "DISPATCH": "#7c3aed",      # 模型派发/切换提示（紫）
    "BOT_BUBBLE": "#f1f5f9",    # 助手气泡底
    "STRIPE": "#f8fafc",        # 列表斑马纹
    "CODE_BLOCK_BG": "#0f172a",  # 代码块深底
    "CODE_BLOCK_FG": "#e2e8f0",  # 代码块文字
}

_DARK = {
    "BG": "#0b0b0c",            # 近黑窗口底（护眼，非纯 #000 减少光晕）
    "PANEL": "#141416",         # 面板、聊天区底（略亮于 BG 分层）
    "BORDER": "#2a2a2e",        # 分隔线
    "TEXT": "#e8e4db",          # 米白主文字
    "MUTED": "#9a958c",         # 次要文字（暖灰，贴米白体系）
    "ACCENT": "#60a5fa",        # 蓝提亮，深底可读
    "ACCENT_SOFT": "#1e293b",   # 用户气泡深蓝灰
    "ACCENT_FAINT": "#1a2332",  # 按钮悬停
    "SUCCESS": "#4ade80",
    "DANGER": "#f87171",
    "DISPATCH": "#a78bfa",
    "BOT_BUBBLE": "#1c1c1f",    # 助手气泡（略亮于 PANEL）
    "STRIPE": "#101012",        # 斑马纹（略暗于 BG）
    "CODE_BLOCK_BG": "#0a0a0b",
    "CODE_BLOCK_FG": "#d6d3cd",
}

# ---------------- 当前生效色板（load() 覆盖；模块级名供全 UI 引用） ----------------
BG = _LIGHT["BG"]
PANEL = _LIGHT["PANEL"]
BORDER = _LIGHT["BORDER"]
TEXT = _LIGHT["TEXT"]
MUTED = _LIGHT["MUTED"]
ACCENT = _LIGHT["ACCENT"]
ACCENT_SOFT = _LIGHT["ACCENT_SOFT"]
ACCENT_FAINT = _LIGHT["ACCENT_FAINT"]
SUCCESS = _LIGHT["SUCCESS"]
DANGER = _LIGHT["DANGER"]
DISPATCH = _LIGHT["DISPATCH"]
BOT_BUBBLE = _LIGHT["BOT_BUBBLE"]
STRIPE = _LIGHT["STRIPE"]
CODE_BLOCK_BG = _LIGHT["CODE_BLOCK_BG"]
CODE_BLOCK_FG = _LIGHT["CODE_BLOCK_FG"]

CURRENT = "light"               # 最近一次 load 的名字


def load(name: str = "light") -> str:
    """按名字切换色板并写回模块级令牌；返回实际生效的名字。

    仅接受 light/dark，其它值回退 light。幂等：可重复调用。
    切换后需重新创建控件（或重启）才会看到新色——启动路径在 apply 之前调用。
    """
    global CURRENT, BG, PANEL, BORDER, TEXT, MUTED, ACCENT, ACCENT_SOFT
    global ACCENT_FAINT, SUCCESS, DANGER, DISPATCH, BOT_BUBBLE, STRIPE
    global CODE_BLOCK_BG, CODE_BLOCK_FG
    key = str(name or "").strip().lower()
    pal = _DARK if key == "dark" else _LIGHT
    CURRENT = "dark" if pal is _DARK else "light"
    BG = pal["BG"]
    PANEL = pal["PANEL"]
    BORDER = pal["BORDER"]
    TEXT = pal["TEXT"]
    MUTED = pal["MUTED"]
    ACCENT = pal["ACCENT"]
    ACCENT_SOFT = pal["ACCENT_SOFT"]
    ACCENT_FAINT = pal["ACCENT_FAINT"]
    SUCCESS = pal["SUCCESS"]
    DANGER = pal["DANGER"]
    DISPATCH = pal["DISPATCH"]
    BOT_BUBBLE = pal["BOT_BUBBLE"]
    STRIPE = pal["STRIPE"]
    CODE_BLOCK_BG = pal["CODE_BLOCK_BG"]
    CODE_BLOCK_FG = pal["CODE_BLOCK_FG"]
    return CURRENT


# ---------------- DWM 标题栏（Windows 系统非客户区） ----------------
# 深灰而非纯黑：与暗色 BORDER 同族，避免顶栏压死画布。
TITLEBAR_DARK_GRAY = "#2f2f31"
_DWMWA_USE_IMMERSIVE_DARK_MODE = 20        # Win10 20H1+
_DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY = 19  # 更早 Win10
_DWMWA_CAPTION_COLOR = 35                  # Win11 自定义标题栏底色（COLORREF）
_DWMWA_TEXT_COLOR = 36                     # Win11 标题栏文字色


def _colorref(hex_color: str) -> int:
    """#rrggbb → COLORREF 0x00BBGGRR（DWM 要求的小端通道序）。"""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return 0
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b << 16) | (g << 8) | r


def apply_title_bar(root) -> bool:
    """Windows 系统标题栏跟随当前色板：dark → 深灰底浅字；light → 系统默认。

    标题栏由 OS/DWM 绘制，Tk 改不了 bg：
    1) DWMWA_USE_IMMERSIVE_DARK_MODE（20，旧版回退 19）切暗色非客户区；
    2) Win11 再设 DWMWA_CAPTION_COLOR / TEXT_COLOR，把标题栏压成深灰（非纯黑）。
    非 Windows / 拿不到 HWND / API 失败：静默返回 False，不阻断启动。
    幂等：可重复调用。需在窗口已创建后调用（launch 在 apply 之后）。
    """
    if sys.platform != "win32" or root is None:
        return False
    try:
        import ctypes
        root.update_idletasks()
        user32 = ctypes.windll.user32
        hwnd = user32.GetParent(int(root.winfo_id()))
        if not hwnd:
            hwnd = int(root.winfo_id())
        if not hwnd:
            return False
        is_dark = CURRENT == "dark"
        dark = ctypes.c_int(1 if is_dark else 0)
        dwm = ctypes.windll.dwmapi
        # 20 = Win10 20H1+；19 = 更早版本。哪个成功用哪个，都失败也忽略。
        for attr in (_DWMWA_USE_IMMERSIVE_DARK_MODE,
                     _DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY):
            try:
                dwm.DwmSetWindowAttribute(
                    ctypes.wintypes.HWND(hwnd) if hasattr(ctypes, "wintypes")
                    else hwnd,
                    attr, ctypes.byref(dark), ctypes.sizeof(dark))
            except Exception:            # noqa: BLE001
                continue
        # Win11：caption/text 显式上色。dark=深灰标题栏；light=还原系统默认。
        try:
            if is_dark:
                cap = ctypes.c_uint(_colorref(TITLEBAR_DARK_GRAY))
                txt = ctypes.c_uint(_colorref(TEXT))
                dwm.DwmSetWindowAttribute(hwnd, _DWMWA_CAPTION_COLOR,
                                          ctypes.byref(cap), ctypes.sizeof(cap))
                dwm.DwmSetWindowAttribute(hwnd, _DWMWA_TEXT_COLOR,
                                          ctypes.byref(txt), ctypes.sizeof(txt))
            else:
                # 0xFFFFFFFF = 交还系统默认（COLORREF 0 会被当成纯黑，不能用）
                reset = ctypes.c_uint(0xFFFFFFFF)
                for attr in (_DWMWA_CAPTION_COLOR, _DWMWA_TEXT_COLOR):
                    dwm.DwmSetWindowAttribute(hwnd, attr,
                                              ctypes.byref(reset),
                                              ctypes.sizeof(reset))
        except Exception:                # noqa: BLE001  旧系统无 35/36 属性
            pass
        return True
    except Exception:                    # noqa: BLE001  标题栏失败不影响主界面
        return False


# 盲文点字等待动画帧（生成中的转圈指示）
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

# ---------------- 间距节奏（px） ----------------
SP_1, SP_2, SP_3, SP_4 = 4, 8, 12, 16

# ---------------- 字号（工具条统一，不能忽大忽小） ----------------
FS_TOOLBAR = 11   # 工具条文字按钮统一字号（模型/语言/字体/附件/发送…）
FS_ICON = 11      # 工具条纯图标按钮统一字号（与文字按钮同大小）
FS_STAT = 9       # 底部统计/状态行统一字号（token 统计、空闲徽标、附件按钮同行同号）


def apply(root, base_font: str = "TkDefaultFont", mono_font: str = "TkFixedFont"):
    """全量应用：窗口底色 + clam 定制（Treeview/滚动条/分栏条/右键菜单）。

    base_font / mono_font 传字体族名（如 ui.FONT_UI），树列表与菜单跟随。
    幂等：重复调用只覆盖同样式。
    """
    root.configure(bg=BG)
    import tkinter.ttk as ttk

    # ---- tk 经典控件默认色（option 仅对未显式 config 的属性生效）----
    # 解决：目录栏 Label、中间 tk.Text 填空框、Frame 白底内边距在暗色下仍是系统白。
    # 必须在 App 构建控件之前调用（launch: load → apply → App）。
    root.option_add("*Frame.Background", BG)
    root.option_add("*Label.Background", BG)
    root.option_add("*Label.Foreground", TEXT)
    root.option_add("*Text.Background", PANEL)
    root.option_add("*Text.Foreground", TEXT)
    # 光标色：Tk 资源名是 insertBackground（camelCase），写错则仍用系统黑
    root.option_add("*Text.InsertBackground", TEXT)
    root.option_add("*Text.SelectBackground", ACCENT)
    root.option_add("*Text.SelectForeground", "#ffffff")
    root.option_add("*Entry.Background", PANEL)
    root.option_add("*Entry.Foreground", TEXT)
    root.option_add("*Entry.InsertBackground", TEXT)
    root.option_add("*Entry.SelectBackground", ACCENT)
    root.option_add("*Entry.SelectForeground", "#ffffff")
    root.option_add("*Spinbox.Background", PANEL)
    root.option_add("*Spinbox.Foreground", TEXT)
    root.option_add("*Spinbox.InsertBackground", TEXT)
    root.option_add("*Listbox.Background", PANEL)
    root.option_add("*Listbox.Foreground", TEXT)
    root.option_add("*Listbox.SelectBackground", ACCENT)
    root.option_add("*Listbox.SelectForeground", "#ffffff")
    root.option_add("*Canvas.Background", BG)
    root.option_add("*Menubutton.Background", BG)
    root.option_add("*Menubutton.Foreground", TEXT)
    root.option_add("*Button.Background", BG)
    root.option_add("*Button.Foreground", TEXT)
    root.option_add("*Button.ActiveBackground", ACCENT_FAINT)
    root.option_add("*Button.ActiveForeground", TEXT)
    # 经典 tk.Scrollbar（ScrolledText 聊天区右侧那条走的是这个，不是 ttk）
    root.option_add("*Scrollbar.Background", BORDER)
    root.option_add("*Scrollbar.TroughColor", PANEL)
    root.option_add("*Scrollbar.ActiveBackground", MUTED)
    root.option_add("*Scrollbar.ActiveForeground", TEXT)
    root.option_add("*Scrollbar.HighlightThickness", 0)
    root.option_add("*Scrollbar.Relief", "flat")
    root.option_add("*Scrollbar.ActiveRelief", "flat")
    root.option_add("*Scrollbar.BorderWidth", 0)
    root.option_add("*Scrollbar.Width", 10)
    root.option_add("*Scrollbar.padX", 0)
    root.option_add("*Scrollbar.takefocus", 0)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:                     # noqa: BLE001  无 clam → 保持默认
        return

    # 树列表：加行高、去边框、选中态用主题色
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground=TEXT, borderwidth=0, relief="flat",
                    rowheight=26, font=(base_font, 10))
    style.map("Treeview",
              background=[("selected", ACCENT_SOFT)],
              foreground=[("selected", TEXT)])
    style.configure("Treeview.Heading", background=PANEL, relief="flat",
                    borderwidth=0, font=(base_font, 10, "bold"))
    style.map("Treeview.Heading", background=[("active", PANEL)])

    # 滚动条：细、无箭头刻痕、浅槽
    style.configure("Vertical.TScrollbar", background=BORDER,
                    troughcolor=PANEL, borderwidth=0, arrowsize=11,
                    gripcount=0)
    style.map("Vertical.TScrollbar",
              background=[("active", MUTED), ("pressed", MUTED)])
    style.configure("Horizontal.TScrollbar", background=BORDER,
                    troughcolor=PANEL, borderwidth=0, gripcount=0)

    # 分栏分隔条：细线化
    style.configure("TPaned", borderwidth=0)

    # 右键/下拉菜单（tk.Menu）：跟随面板底、无立体边框、主题色悬停
    root.option_add("*Menu.background", PANEL)
    root.option_add("*Menu.foreground", TEXT)
    root.option_add("*Menu.borderWidth", 1)
    root.option_add("*Menu.activeBorderWidth", 0)
    root.option_add("*Menu.activeBackground", ACCENT_FAINT)
    root.option_add("*Menu.font", (base_font, 10))

    # ttk Entry / Spinbox（右栏搜索、缓存 TTL 等未手写 tk.Entry 的输入）
    style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT,
                    insertcolor=TEXT, borderwidth=0, lightcolor=PANEL,
                    darkcolor=PANEL, padding=(6, 4))
    style.map("TEntry",
              fieldbackground=[("disabled", BG), ("readonly", PANEL)],
              foreground=[("disabled", MUTED)],
              bordercolor=[("focus", ACCENT), ("!focus", BORDER)])
    style.configure("TSpinbox", fieldbackground=PANEL, foreground=TEXT,
                    arrowcolor=TEXT, borderwidth=0, padding=(4, 3))
    style.map("TSpinbox",
              fieldbackground=[("disabled", BG)],
              foreground=[("disabled", MUTED)],
              arrowcolor=[("disabled", MUTED)])

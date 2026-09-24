# -*- coding: utf-8 -*-
"""theme.py：LIGHT/DARK 色板切换 + 模块级令牌 + 系统标题栏。"""

import theme


class _StubRoot:
    """无真实 Tk 窗口：winfo_id/update_idletasks 空实现。"""

    def winfo_id(self):
        return 0

    def update_idletasks(self):
        pass


def test_default_palette_is_light():
    theme.load("light")
    assert theme.CURRENT == "light"
    assert theme.BG == theme._LIGHT["BG"]
    assert theme.TEXT == theme._LIGHT["TEXT"]


def test_load_dark_switches_tokens():
    theme.load("dark")
    try:
        assert theme.CURRENT == "dark"
        assert theme.BG == theme._DARK["BG"]
        assert theme.PANEL == theme._DARK["PANEL"]
        assert theme.TEXT == theme._DARK["TEXT"]
        # 黑底米白字：TEXT 不能还是浅色体系的深蓝黑
        assert theme.TEXT != theme._LIGHT["TEXT"]
        assert theme.BG != theme._LIGHT["BG"]
    finally:
        theme.load("light")


def test_load_unknown_falls_back_to_light():
    assert theme.load("blue") == "light"
    assert theme.load("") == "light"
    assert theme.load(None) == "light"
    assert theme.CURRENT == "light"


def test_load_is_idempotent():
    theme.load("dark")
    try:
        bg1, text1 = theme.BG, theme.TEXT
        theme.load("dark")
        assert (theme.BG, theme.TEXT) == (bg1, text1)
    finally:
        theme.load("light")


def test_apply_title_bar_safe_on_stub_and_none():
    # 无窗口 / root=None：不抛，返回 False（或非 win32 上 False）
    assert theme.apply_title_bar(None) is False
    assert isinstance(theme.apply_title_bar(_StubRoot()), bool)


def test_titlebar_dark_gray_is_not_pure_black():
    # 深灰标题栏：与暗色 BORDER 同族，禁止 #000
    assert theme.TITLEBAR_DARK_GRAY.startswith("#")
    assert len(theme.TITLEBAR_DARK_GRAY) == 7
    assert theme.TITLEBAR_DARK_GRAY.lower() != "#000000"


def test_colorref_is_bgr_packed():
    # COLORREF = 0x00BBGGRR（DWM 小端通道序）
    assert theme._colorref("#000000") == 0
    assert theme._colorref("#ffffff") == 0x00FFFFFF
    assert theme._colorref("#2f2f31") == 0x312F2F


def test_apply_registers_classic_scrollbar_defaults():
    """ScrolledText 聊天滚动条是经典 tk.Scrollbar，靠 option_add 上灰。"""
    import tkinter as tk
    root = tk.Tk()
    try:
        root.withdraw()
        theme.load("dark")
        theme.apply(root, base_font="TkDefaultFont", mono_font="TkFixedFont")
        sb = tk.Scrollbar(root)
        assert str(sb.cget("background")) == theme.BORDER
        assert str(sb.cget("troughcolor")) == theme.PANEL
        assert str(sb.cget("activebackground")) == theme.MUTED
        sb.destroy()
    finally:
        theme.load("light")
        root.destroy()


def test_apply_text_insert_background_is_theme_text():
    """光标 insertBackground 必须跟 TEXT，暗色下不能是系统黑。"""
    import tkinter as tk
    root = tk.Tk()
    try:
        root.withdraw()
        theme.load("dark")
        theme.apply(root, base_font="TkDefaultFont", mono_font="TkFixedFont")
        txt = tk.Text(root)
        assert str(txt.cget("insertbackground")) == theme.TEXT
        assert theme.TEXT == theme._DARK["TEXT"]
        assert theme.TEXT.lower() != "#000000"
        txt.destroy()
        ent = tk.Entry(root)
        assert str(ent.cget("insertbackground")) == theme.TEXT
        ent.destroy()
    finally:
        theme.load("light")
        root.destroy()

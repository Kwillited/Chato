# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 添加前端构建后的静态文件
added_files = [
    ('web_dist', '.'),
    ('backend/config', 'config'),
    ('backend/app', 'app'),
    ('backend/main.py', '.'),
]

a = Analysis(['backend/webview_main.py'],
             pathex=['backend'],
             binaries=[],
             datas=added_files,
             hiddenimports=[
                 'pydantic_settings',
                 'langchain_community',
                 'langchain_openai',
                 'langchain_anthropic',
                 'langchain_google_genai',
                 'langchain_huggingface',
                 'langchain_deepseek',
                 'sentence_transformers',
                 'uvicorn',
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

executable = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='Chato',
              debug=True,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=True)

coll = COLLECT(executable,
             a.binaries,
             a.zipfiles,
             a.datas,
             strip=False,
             upx=True,
             upx_exclude=[],
             name='Chato')
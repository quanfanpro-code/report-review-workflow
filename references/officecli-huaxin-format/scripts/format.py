# format.py — 四川华信(集团)会计师事务所审计报告格式强制器（OfficeCLI 版）
# 用法：python format.py in.docx [out.docx]
# ponytail: 单文件、零依赖（仅 stdlib + officecli），函数式流水线。

import subprocess, json, re, sys, os, shutil, tempfile

def _find_officecli():
    """Locate officecli: env OFFICECLI > PATH > default install path."""
    env = os.environ.get('OFFICECLI')
    if env and os.path.isfile(env):
        return env
    found = shutil.which('officecli')
    if found:
        return found
    default = r'C:\Users\27651\AppData\Local\OfficeCLI\officecli.exe'
    if os.path.isfile(default):
        return default
    raise FileNotFoundError(
        'officecli not found. Install it or set OFFICECLI env var.'
    )

OFFICECLI = _find_officecli()

# --- 正则（与原 .NET 版 Program.cs 完全同步）---
CN_NUM   = re.compile(r'^[一二三四五六七八九十百千零两]+[、．.]')
CN_PAREN = re.compile(r'^[（(][一二三四五六七八九十百千零]+[）)]')
AR_NUM   = re.compile(r'^\d+[.．、]')
DATE_RE  = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日|二[〇零O0-9二三四五六七八九十]+年.*月.*日')

# --- 常量（OfficeCLI 使用 pt，不是半磅 / twips）---
# 半磅→pt: ÷2。BODY_SZ=24 半磅=12pt, TITLE_SZ=32 半磅=16pt, HDR_SZ=21 半磅=10.5pt
BODY_SZ  = 12     # 12pt 小四（原 24 半磅）
TITLE_SZ = 16     # 16pt 三号（原 32 半磅）
HDR_SZ   = 10.5   # 10.5pt 五号（原 21 半磅）

# 行距：exact 模式用 pt 后缀，auto 模式用倍数后缀
BODY_LINE = "21pt"    # 固定 21 磅（原 420 缇）
HEAD_LINE = "1.5x"    # 1.5 倍（原 360）
SIGN_LINE = "42pt"    # 落款 42 磅（原 840 缇）
INDENT2   = 480   # 2 字符
INDENT4   = 960   # 4 字符
M_TOP     = 1417; M_BOTTOM = 1701; M_LEFT = 1417; M_RIGHT = 850
COVER_BOTTOM = 1247
HDR_DIST  = 850; FTR_DIST = 567
A4W = 11906; A4H = 16838
CPA_TAB   = 7200  # 右对齐制表位


def run(*args, strict=False):
    """Run officecli, return (stdout, stderr). strict=True → raise on failure."""
    cmd = [OFFICECLI] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        msg = f"officecli {' '.join(args[:4])}... exit={r.returncode}"
        if strict:
            raise RuntimeError(msg + f"\n  stderr: {r.stderr.strip()[:300]}")
        print(f"[warn] {msg}: {r.stderr.strip()[:200]}", file=sys.stderr)
    return r.stdout.strip(), r.stderr.strip()


def run_json(*args):
    """Run officecli --json, parse."""
    out, _ = run(*(list(args) + ['--json']))
    if not out:
        return None
    return json.loads(out)


def _body_children(docx):
    """Defensively extract top-level children from get /body JSON response.
    Returns [] on any schema mismatch — the caller handles empty gracefully.
    """
    body = run_json('get', docx, '/body')
    if not body:
        return []
    try:
        return body['data']['results'][0]['children']
    except (KeyError, IndexError, TypeError):
        return []


def insert_infix(path, infix):
    d, f = os.path.split(path)
    name, ext = os.path.splitext(f)
    return os.path.join(d, f"{name}{infix}{ext}")


def is_number(s):
    """Check if a string can be parsed as a number, ignoring commas, %, parentheses."""
    if not s or not s.strip():
        return False
    c = s.strip().replace(',', '').replace('%', '').replace('(', '-').replace(')', '')
    try:
        float(c)
        return True
    except ValueError:
        return False


def format_number(raw):
    """千分位两位小数；零值/单独横杠→空；负数取正加负号；%保留。"""
    s = raw.strip()
    if s in ('0', '-', ''):
        return ''
    pct = s.endswith('%')
    neg = (s.startswith('(') and s.endswith(')')) or s.startswith('-')
    s = s.replace('%', '').replace(',', '').replace('(', '').replace(')', '').replace('-', '')
    try:
        v = float(s)
    except ValueError:
        return raw.strip()
    if neg:
        v = -v
    result = f"{v:,.2f}"
    return result + '%' if pct else result


def is_salutation(text):
    t = text.strip()
    if not (t.endswith('：') or t.endswith(':')):
        return False
    keywords = ('公司', '集团', '委员会', '事务所', '研究院', '中心', '学校', '银行')
    return any(k in t for k in keywords)


def detect_cover(docx):
    """扫描前 60 个元素，找含四关键词的表格。"""
    children = _body_children(docx)
    if not children:
        return False
    count = 0
    for child in children:
        for d in _walk_texts(child):
            count += 1
            if count > 60:
                return False
            txt = d.get('text', '') or ''
            if ('会计师事务所' in txt and '地址' in txt and '电话' in txt and '传真' in txt
                    and child.get('type') == 'table'):
                return True
    return False


def _walk_texts(node):
    """Recursively yield all descendant nodes (for keyword scanning)."""
    yield node
    for child in node.get('children', []):
        yield from _walk_texts(child)


def get_top_paragraphs(docx):
    """Get top-level paragraphs from /body, return list of (path, text, node)."""
    results = []
    for child in _body_children(docx):
        if child.get('type') == 'paragraph':
            path = child.get('path', '')
            text = child.get('text', '') or ''
            results.append((path, text, child))
    return results


def get_tables(docx):
    """Get top-level tables from /body, return list of (path, node)."""
    return [(c.get('path', ''), c) for c in _body_children(docx) if c.get('type') == 'table']


def classify_paragraphs(paras):
    """
    Classify each paragraph as: title, docno, salutation, h1, h2, h3, signature, body.
    Returns list of (path, text, role, meta). meta includes normalized text for h3.
    Title detection: first up to 3 non-empty paragraphs at top, BREAK on any pattern match
    (mirrors .NET DetectTitle exactly).
    """
    result = []
    sig_start = None
    title_done = False
    taken_title = 0

    # Find signature block start
    for i, (path, text, _) in enumerate(paras):
        if '四川华信' in text:
            sig_start = i
            break

    for i, (path, text, _) in enumerate(paras):
        t = text.strip()
        role = None
        meta = {}

        # Empty paragraph → body
        if not t:
            result.append((path, text, 'body', meta))
            continue

        # Title scan (only at top, before any pattern match)
        if not title_done and taken_title < 3:
            is_pattern = (CN_NUM.match(t) or CN_PAREN.match(t) or AR_NUM.match(t)
                          or '川华信' in t or '四川华信' in t or is_salutation(t))
            if is_pattern:
                title_done = True   # break title scanning, fall through to normal classify
            else:
                role = 'title'
                taken_title += 1
                result.append((path, text, role, meta))
                continue

        # Doc number
        if '川华信' in t and len(t) <= 50 and '事务所' not in t:
            role = 'docno'
        # Salutation
        elif is_salutation(t):
            role = 'salutation'
        # h1: 一、二、...
        elif CN_NUM.match(t):
            role = 'h1'
        # h2: （一）（二）...
        elif CN_PAREN.match(t):
            role = 'h2'
        # h3: 1. 2、3．
        elif AR_NUM.match(t):
            role = 'h3'
            # 编号分隔符归一：1. / 1、 → 1．
            m = re.match(r'^(\d+)([.、．])', t)
            if m and m.group(2) != '．':
                meta['normalized_text'] = m.group(1) + '．' + t[m.end():]
        # Signature block
        elif sig_start is not None and i >= sig_start:
            if DATE_RE.search(t):
                role = 'sig_date'
            elif '中国注册会计师' in t:
                role = 'sig_cpa'
            else:
                role = 'signature'
        # Body
        else:
            role = 'body'

        result.append((path, text, role, meta))

    return result


def build_batch(classified, docx):
    """Generate batch JSON array for paragraph-level formatting."""
    commands = []

    for path, text, role, meta in classified:
        if role in ('title', 'docno', 'salutation', 'h1', 'h2', 'h3', 'body'):
            props = paragraph_props(role, meta)
            # Apply normalized text for h3
            norm_text = meta.get('normalized_text')
            if norm_text:
                props['text'] = norm_text
            commands.append({'command': 'set', 'path': path, 'props': props})

    return commands


def paragraph_props(role, meta):
    """Return props dict for a given paragraph role. All values are strings."""
    B = 'true'
    NB = 'false'

    if role == 'title':
        return {
            'align': 'center', 'lineSpacing': str(HEAD_LINE), 'lineRule': 'auto',
            'spaceBefore': '120', 'spaceAfter': '120',
            'size': str(TITLE_SZ), 'bold': B,
            'font': 'Times New Roman', 'font.ea': '宋体',
        }
    elif role == 'docno':
        return {
            'align': 'right', 'lineSpacing': str(HEAD_LINE), 'lineRule': 'auto',
            'spaceBefore': '60', 'spaceAfter': '60',
            'size': str(BODY_SZ), 'bold': NB,
            'font': 'Times New Roman', 'font.ea': '宋体',
        }
    elif role == 'salutation':
        return {
            'align': 'left', 'lineSpacing': str(HEAD_LINE), 'lineRule': 'auto',
            'spaceBefore': '0', 'spaceAfter': '0',
            'size': str(BODY_SZ), 'bold': B,
            'font': 'Times New Roman', 'font.ea': '宋体',
        }
    elif role == 'h1':
        return {
            'align': 'both', 'lineSpacing': str(HEAD_LINE), 'lineRule': 'auto',
            'spaceBefore': '240', 'spaceAfter': '120',
            'size': str(BODY_SZ), 'bold': B,
            'font': 'Times New Roman', 'font.ea': '宋体',
            'outlineLvl': '0',
        }
    elif role == 'h2':
        return {
            'align': 'both', 'lineSpacing': str(HEAD_LINE), 'lineRule': 'auto',
            'spaceBefore': '120', 'spaceAfter': '60',
            'size': str(BODY_SZ), 'bold': B,
            'font': 'Times New Roman', 'font.ea': '宋体',
            'outlineLvl': '1',
        }
    elif role == 'h3':
        return {
            'align': 'both', 'lineSpacing': str(HEAD_LINE), 'lineRule': 'auto',
            'firstLineIndent': str(INDENT2), 'spaceBefore': '60', 'spaceAfter': '0',
            'size': str(BODY_SZ), 'bold': B,
            'font': 'Times New Roman', 'font.ea': '宋体',
            'outlineLvl': '2',
        }
    else:  # body
        return {
            'align': 'both', 'lineSpacing': str(BODY_LINE), 'lineRule': 'exact',
            'firstLineIndent': str(INDENT2), 'spaceBefore': '0', 'spaceAfter': '0',
            'size': str(BODY_SZ), 'bold': NB, 'italic': NB, 'underline': 'none',
            'font': 'Times New Roman', 'font.ea': '宋体',
        }


def execute_batch(docx, commands):
    """Write batch JSON to temp file and execute via officecli batch."""
    if not commands:
        return
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False,
                                      encoding='utf-8') as f:
        json.dump(commands, f, ensure_ascii=False)
        tmp = f.name
    try:
        run('batch', docx, '--input', tmp)
    finally:
        os.unlink(tmp)


def format_tables(docx):
    """Set table borders + header row + cell formatting."""
    tables = get_tables(docx)
    for tbl_path, tbl_node in tables:
        # Table borders: top/bottom single, left/right none, inside dashed
        run('set', docx, tbl_path,
            '--prop', 'border.top=single;0.75pt;000000',
            '--prop', 'border.bottom=single;0.75pt;000000',
            '--prop', 'border.left=none',
            '--prop', 'border.right=none',
            '--prop', 'border.horizontal=dashed;0.75pt;000000',
            '--prop', 'border.vertical=dashed;0.75pt;000000',
            '--prop', 'width=100%')

        # Header row
        rows = tbl_node.get('children', [])
        if rows:
            first_row_path = rows[0].get('path', '')
            if first_row_path:
                run('set', docx, first_row_path, '--prop', 'header=true')

        # Cell formatting
        for r_idx, row in enumerate(rows):
            cells = row.get('children', [])
            for c_idx, cell in enumerate(cells):
                cell_path = cell.get('path', '')
                cell_text = cell.get('text', '') or ''
                is_header = (r_idx == 0)
                is_first_col = (c_idx == 0)

                if is_header:
                    align = 'center'
                elif is_first_col:
                    align = 'left'
                elif is_number(cell_text):
                    align = 'right'
                else:
                    align = 'center'

                run('set', docx, cell_path,
                    '--prop', f'align={align}',
                    '--prop', 'valign=center',
                    '--prop', f'size={BODY_SZ}',
                    '--prop', 'bold=false',
                    '--prop', 'italic=false',
                    '--prop', 'lineSpacing=12pt',
                    '--prop', 'lineRule=exact',
                    '--prop', 'padding.top=0',
                    '--prop', 'padding.bottom=0',
                    '--prop', 'font=Times New Roman',
                    '--prop', 'font.ea=宋体')

                # Number formatting for non-header, non-first-col, numeric cells
                if not is_header and not is_first_col and is_number(cell_text):
                    formatted = format_number(cell_text)
                    if formatted or cell_text.strip() in ('0', '-'):
                        run('set', docx, cell_path, '--prop', f'text={formatted}')


def format_signature(docx):
    """落款区：42磅行距、三级台阶、日期右对齐、CPA右Tab。"""
    paras = get_top_paragraphs(docx)
    sig_start = None
    for i, (path, text, _) in enumerate(paras):
        if '四川华信' in text:
            sig_start = i
            break
    if sig_start is None:
        return

    # Ponytail: find the first "四川华信" paragraph, treat it + next 2 as the 3-step ladder
    ladder_indents = ['0', str(INDENT2), str(INDENT4)]
    for k in range(min(3, len(paras) - sig_start)):
        path, _, _, = paras[sig_start + k]
        # Set ladder indent + signature line spacing
        run('set', docx, path,
            '--prop', f'firstLineIndent={ladder_indents[k]}',
            '--prop', f'lineSpacing={SIGN_LINE}',
            '--prop', 'lineRule=exact',
            '--prop', 'spaceBefore=0',
            '--prop', 'spaceAfter=0',
            '--prop', f'size={BODY_SZ}',
            '--prop', 'font=Times New Roman',
            '--prop', 'font.ea=宋体')

    # Remaining signature block paragraphs: 42磅行距
    for i in range(sig_start + 3, len(paras)):
        path, text, _, = paras[i]
        if DATE_RE.search(text):
            run('set', docx, path,
                '--prop', f'lineSpacing={SIGN_LINE}',
                '--prop', 'lineRule=exact',
                '--prop', 'align=right',
                '--prop', f'size={BODY_SZ}',
                '--prop', 'font=Times New Roman',
                '--prop', 'font.ea=宋体')
            break  # date is the last line
        else:
            run('set', docx, path,
                '--prop', f'lineSpacing={SIGN_LINE}',
                '--prop', 'lineRule=exact',
                '--prop', f'size={BODY_SZ}',
                '--prop', 'font=Times New Roman',
                '--prop', 'font.ea=宋体')

    # CPA right tab stop via raw-set — target pPr of matching paragraphs
    for i in range(sig_start, len(paras)):
        path, text, node = paras[i]
        if '中国注册会计师' in text:
            para_id = node.get('format', {}).get('paraId', '')
            if para_id:
                xpath = f'//w:p[@w14:paraId="{para_id}"]/w:pPr'
            else:
                # ponytail: fallback to positional index — fragile, log a warning
                xpath = f'//w:body/w:p[{i + 1}]/w:pPr'
                print(f"  [warn] CPA tab: paraId missing for p[{i+1}], using positional fallback", file=sys.stderr)
            xml_frag = '<w:tabs><w:tab w:val="right" w:pos="7200"/></w:tabs>'
            run('raw-set', docx, '/document', '--xpath', xpath,
                '--action', 'append', '--xml', xml_frag)


def apply_page_setup(docx):
    """Set A4 + margins. Use --json but ignore errors (section may not exist for empty docs)."""
    run('set', docx, '/section[1]',
        '--prop', f'pageWidth={A4W}',
        '--prop', f'pageHeight={A4H}',
        '--prop', f'marginTop={M_TOP}',
        '--prop', f'marginBottom={M_BOTTOM}',
        '--prop', f'marginLeft={M_LEFT}',
        '--prop', f'marginRight={M_RIGHT}',
        '--prop', f'marginHeader={HDR_DIST}',
        '--prop', f'marginFooter={FTR_DIST}')


def apply_styles(docx):
    """Set Normal style + DocDefaults."""
    # DocDefaults
    run('set', docx, '/',
        '--prop', 'docDefaults.font=Times New Roman',
        '--prop', 'docDefaults.font.eastAsia=宋体',
        '--prop', f'docDefaults.fontSize={BODY_SZ}')
    # Normal style
    run('set', docx, '/styles/Normal',
        '--prop', 'font=Times New Roman',
        '--prop', 'font.ea=宋体',
        '--prop', f'size={BODY_SZ}',
        '--prop', 'bold=false',
        '--prop', f'lineSpacing={BODY_LINE}',
        '--prop', 'lineRule=exact',
        '--prop', 'align=both')


def _ensure_single_part(docx, kind):
    """ponytail: remove existing header/footer, ignore if none. Then caller re-adds."""
    run('remove', docx, f'/{kind}[1]')


def apply_header_footer(docx):
    """Set header/footer: 10.5pt, header left with bottom border, footer centered with PAGE."""
    _ensure_single_part(docx, 'header')
    _ensure_single_part(docx, 'footer')

    run('add', docx, '/', '--type', 'header', '--prop', 'type=default',
        '--prop', f'size={HDR_SZ}', '--prop', 'font=Times New Roman',
        '--prop', 'align=left', strict=True)

    # ponytail: header bottom border not exposed via high-level API — use raw-set
    run('raw-set', docx, '/header[1]', '--xpath', '//w:p/w:pPr',
        '--action', 'append',
        '--xml', '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>')

    run('add', docx, '/', '--type', 'footer', '--prop', 'type=default',
        '--prop', f'size={HDR_SZ}', '--prop', 'font=Times New Roman',
        '--prop', 'align=center', '--prop', 'field=page', strict=True)


def apply_char_cleanup(docx):
    """Remove char-level pollution: w:w, spacing, position, kern, i, u from all runs."""
    # ponytail: single XPath union targeting all 6 element types at once
    xpath = ('//w:r/w:rPr/w:w | //w:r/w:rPr/w:spacing | //w:r/w:rPr/w:position '
             '| //w:r/w:rPr/w:kern | //w:r/w:rPr/w:i | //w:r/w:rPr/w:u')
    run('raw-set', docx, '/document', '--xpath', xpath, '--action', 'remove')


def main():
    if len(sys.argv) < 2:
        print("usage: python format.py in.docx [out.docx]")
        print("  out.docx defaults to in_huaxin_cli.docx (original preserved)")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"[FATAL] input not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    output_file = sys.argv[2] if len(sys.argv) > 2 else insert_infix(input_file, '_huaxin_cli')
    if os.path.exists(output_file):
        print(f"  output exists, will overwrite: {os.path.basename(output_file)}")

    # Copy
    shutil.copy2(input_file, output_file)
    print(f"processing: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")

    try:
        # Cover detection
        is_cover = detect_cover(output_file)
        if is_cover:
            print("  cover detected: margins only (cover bottom=2.2cm)")
            run('set', output_file, '/section[1]',
                '--prop', f'marginTop={M_TOP}',
                '--prop', f'marginBottom={COVER_BOTTOM}',
                '--prop', f'marginLeft={M_LEFT}',
                '--prop', f'marginRight={M_RIGHT}',
                '--prop', f'marginHeader={HDR_DIST}',
                '--prop', f'marginFooter={FTR_DIST}',
                '--prop', f'pageWidth={A4W}',
                '--prop', f'pageHeight={A4H}', strict=True)
            print(f"done: {output_file}")
            return

        # Get paragraphs
        paras = get_top_paragraphs(output_file)
        if not paras:
            print("  no paragraphs found — treating as empty doc, applying page + styles only")
            apply_page_setup(output_file)
            apply_styles(output_file)
            print(f"done: {output_file}")
            return

        # Classify
        classified = classify_paragraphs(paras)
        roles = [r for _, _, r, _ in classified]
        print(f"  paragraphs: {len(paras)} ({', '.join(f'{r}={roles.count(r)}' for r in ['title','h1','h2','h3','body','docno','salutation','signature'] if roles.count(r))})")

        # Build and execute batch
        commands = build_batch(classified, output_file)
        if commands:
            execute_batch(output_file, commands)
            print(f"  batch executed: {len(commands)} commands")

        # Tables
        format_tables(output_file)

        # Signature block
        format_signature(output_file)

        # Page setup + styles
        apply_page_setup(output_file)
        apply_styles(output_file)

        # Header/footer
        apply_header_footer(output_file)

        # Char cleanup
        apply_char_cleanup(output_file)

        print(f"done: {output_file}")

    except RuntimeError as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

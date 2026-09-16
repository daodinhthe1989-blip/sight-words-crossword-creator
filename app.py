import random
from datetime import datetime
from io import BytesIO

import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------
PASSWORD_EXPIRY = {"KDPCW2026": None}

st.set_page_config(page_title="KDPEasy Crossword Creator", page_icon="\U0001F9E9", layout="wide")


def check_password() -> bool:
    if st.session_state.get("authed"):
        return True
    st.title("KDPEasy Crossword Creator")
    pw = st.text_input("Enter your access password", type="password")
    if pw:
        if pw in PASSWORD_EXPIRY:
            expiry = PASSWORD_EXPIRY[pw]
            if expiry is None or datetime.now() < expiry:
                st.session_state["authed"] = True
                st.rerun()
            else:
                st.error("This password has expired.")
        else:
            st.error("Incorrect password.")
    return False


# ---------------------------------------------------------------------------
# Word bank (starter set for v1 - Level 1 / Level 2, expand later to full
# Fry 1000-word tiers per project_tool9_crosswordcreator memory)
# ---------------------------------------------------------------------------
WORD_BANK = {
    "Level 1 (Easy)": [
        {"word": "SEE", "clue": "I can ___ the bird in the tree."},
        {"word": "RUN", "clue": "I like to ___ in the park."},
        {"word": "JUMP", "clue": "The frog can ___ very high."},
        {"word": "STOP", "clue": "Please ___ before you cross the street."},
        {"word": "LOOK", "clue": "___ both ways before you cross."},
        {"word": "PLAY", "clue": "Let's go ___ outside."},
        {"word": "HELP", "clue": "Can you ___ me carry this bag?"},
        {"word": "COME", "clue": "Please ___ here right now."},
        {"word": "MAKE", "clue": "I want to ___ a sandwich."},
        {"word": "GOOD", "clue": "You did a ___ job!"},
        {"word": "BLUE", "clue": "The sky is ___."},
        {"word": "FUNNY", "clue": "That joke was really ___."},
        {"word": "LITTLE", "clue": "The puppy is very ___."},
        {"word": "YELLOW", "clue": "The sun looks ___."},
        {"word": "WHERE", "clue": "___ is my backpack?"},
        {"word": "THREE", "clue": "I have ___ apples."},
        {"word": "AWAY", "clue": "The cat ran ___."},
        {"word": "FIND", "clue": "Can you ___ my shoes?"},
        {"word": "DOWN", "clue": "Please sit ___."},
        {"word": "BIG", "clue": "That is a ___ elephant."},
        {"word": "RED", "clue": "The apple is ___."},
        {"word": "EAT", "clue": "I like to ___ pizza."},
        {"word": "SAY", "clue": "___ hello to your friend."},
        {"word": "RIDE", "clue": "I like to ___ my bike."},
        {"word": "SOON", "clue": "We will leave ___."},
        {"word": "WENT", "clue": "Yesterday I ___ to school."},
        {"word": "WANT", "clue": "I ___ a new toy."},
        {"word": "LIKE", "clue": "I ___ ice cream."},
        {"word": "SAW", "clue": "I ___ a rainbow yesterday."},
        {"word": "WELL", "clue": "You are doing very ___."},
        {"word": "WHAT", "clue": "___ is your name?"},
        {"word": "WITH", "clue": "I went to the park ___ my dad."},
        {"word": "THIS", "clue": "___ is my favorite book."},
        {"word": "THAT", "clue": "Look at ___ big dog over there."},
        {"word": "THEY", "clue": "___ are my best friends."},
        {"word": "THERE", "clue": "Put the box over ___."},
        {"word": "WHO", "clue": "___ is knocking at the door?"},
        {"word": "NOW", "clue": "We need to go ___."},
        {"word": "OUT", "clue": "Let's go ___ to play."},
        {"word": "NEW", "clue": "I got a ___ pair of shoes."},
    ],
    "Level 2 (Medium)": [
        {"word": "NEVER", "clue": "I have ___ seen a real lion."},
        {"word": "ALWAYS", "clue": "I ___ brush my teeth at night."},
        {"word": "BETWEEN", "clue": "The cat is sitting ___ the two chairs."},
        {"word": "CLEAN", "clue": "Please ___ your room."},
        {"word": "WRITE", "clue": "I will ___ a letter to my friend."},
        {"word": "TRY", "clue": "Please ___ your best on the test."},
        {"word": "THANK", "clue": "I want to ___ you for the gift."},
        {"word": "FAR", "clue": "The store is not ___ from here."},
        {"word": "PICK", "clue": "Please ___ your favorite color."},
        {"word": "FOUND", "clue": "I ___ my missing sock."},
        {"word": "LAUGH", "clue": "The movie made everyone ___."},
        {"word": "PLEASE", "clue": "___ pass the salt."},
        {"word": "WALK", "clue": "We like to ___ to school."},
        {"word": "EIGHT", "clue": "I have ___ crayons in my box."},
        {"word": "DRINK", "clue": "I need to ___ some water."},
        {"word": "GROW", "clue": "Plants ___ when you water them."},
        {"word": "FINISH", "clue": "I need to ___ my homework."},
        {"word": "TOGETHER", "clue": "We baked cookies ___."},
        {"word": "TODAY", "clue": "___ is a beautiful day."},
        {"word": "SMALL", "clue": "The kitten is very ___."},
        {"word": "DONE", "clue": "I am ___ with my homework."},
        {"word": "WILL", "clue": "I ___ see you tomorrow."},
        {"word": "LONG", "clue": "The river is very ___."},
        {"word": "BEFORE", "clue": "Wash your hands ___ you eat."},
        {"word": "AFTER", "clue": "We will play ___ dinner."},
        {"word": "AROUND", "clue": "We walked ___ the park."},
        {"word": "ABOVE", "clue": "The plane flew ___ the clouds."},
        {"word": "BELOW", "clue": "The fish swim ___ the boat."},
        {"word": "INSIDE", "clue": "Let's go ___ because it's cold."},
        {"word": "OUTSIDE", "clue": "The kids are playing ___."},
        {"word": "MORNING", "clue": "I eat breakfast every ___."},
        {"word": "NIGHT", "clue": "The stars come out at ___."},
        {"word": "FRIEND", "clue": "She is my best ___."},
        {"word": "HAPPY", "clue": "The puppy looks so ___."},
        {"word": "SAD", "clue": "He felt ___ when his toy broke."},
        {"word": "ANGRY", "clue": "She was ___ when she lost the game."},
        {"word": "SLEEPY", "clue": "The baby looks very ___."},
        {"word": "HUNGRY", "clue": "I am ___, let's eat."},
        {"word": "THIRSTY", "clue": "I am ___, I need water."},
        {"word": "GENTLE", "clue": "Please be ___ with the puppy."},
    ],
}

TRIM_SIZES = {
    "Letter (8.5 x 11 in)": (8.5, 11.0),
    "Square (8.5 x 8.5 in)": (8.5, 8.5),
    "8 x 10 in": (8.0, 10.0),
    "6 x 9 in": (6.0, 9.0),
    "A4": (8.27, 11.69),
    "A5": (5.83, 8.27),
}


def get_word_pool(level_choice: str) -> list:
    if level_choice == "Mixed (Level 1 + 2)":
        return WORD_BANK["Level 1 (Easy)"] + WORD_BANK["Level 2 (Medium)"]
    return WORD_BANK[level_choice]


# ---------------------------------------------------------------------------
# Crossword generation engine (pure algorithm, no AI)
# ---------------------------------------------------------------------------
def _can_place(occupied, word, row, col, direction):
    if direction == "A":
        cells = [(row, col + i) for i in range(len(word))]
        before, after = (row, col - 1), (row, col + len(word))
    else:
        cells = [(row + i, col) for i in range(len(word))]
        before, after = (row - 1, col), (row + len(word), col)

    if before in occupied or after in occupied:
        return None

    intersections = 0
    for (r, c), ch in zip(cells, word):
        if (r, c) in occupied:
            if occupied[(r, c)] != ch:
                return None
            intersections += 1
        else:
            perp = [(r - 1, c), (r + 1, c)] if direction == "A" else [(r, c - 1), (r, c + 1)]
            for p in perp:
                if p in occupied:
                    return None
    return intersections


def _place_word(occupied, word, row, col, direction):
    if direction == "A":
        for i, ch in enumerate(word):
            occupied[(row, col + i)] = ch
    else:
        for i, ch in enumerate(word):
            occupied[(row + i, col)] = ch


def _attempt_layout(entries, target_count, rng):
    pool = list(entries)
    rng.shuffle(pool)
    pool.sort(key=lambda e: -len(e["word"]))

    occupied = {}
    placed = []

    first = pool[0]
    _place_word(occupied, first["word"], 0, 0, "A")
    placed.append({"word": first["word"], "clue": first["clue"], "row": 0, "col": 0, "dir": "A"})

    remaining = pool[1:]
    rng.shuffle(remaining)

    for cand in remaining:
        if len(placed) >= target_count:
            break
        word = cand["word"]
        if word in (p["word"] for p in placed):
            continue
        candidates = []
        for (r, c), ch in occupied.items():
            for i, wch in enumerate(word):
                if wch == ch:
                    candidates.append((r, c - i, "A"))
                    candidates.append((r - i, c, "D"))
        rng.shuffle(candidates)
        best = None
        for row, col, direction in candidates:
            score = _can_place(occupied, word, row, col, direction)
            if score and score >= 1:
                best = (row, col, direction)
                break
        if best:
            _place_word(occupied, word, *best)
            placed.append({"word": word, "clue": cand["clue"], "row": best[0], "col": best[1], "dir": best[2]})

    return occupied, placed


def _normalize(occupied, placed):
    rows = [r for r, _ in occupied]
    cols = [c for _, c in occupied]
    min_r, min_c = min(rows), min(cols)
    new_occupied = {(r - min_r, c - min_c): ch for (r, c), ch in occupied.items()}
    new_placed = [{**p, "row": p["row"] - min_r, "col": p["col"] - min_c} for p in placed]
    n_rows = max(rows) - min_r + 1
    n_cols = max(cols) - min_c + 1
    return new_occupied, new_placed, n_rows, n_cols


def _assign_numbers(occupied, placed, n_rows, n_cols):
    number_map = {}
    next_num = 1
    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) not in occupied:
                continue
            starts_across = (c == 0 or (r, c - 1) not in occupied) and (c + 1 < n_cols and (r, c + 1) in occupied)
            starts_down = (r == 0 or (r - 1, c) not in occupied) and (r + 1 < n_rows and (r + 1, c) in occupied)
            if starts_across or starts_down:
                number_map[(r, c)] = next_num
                next_num += 1
    for p in placed:
        p["number"] = number_map[(p["row"], p["col"])]
    return placed, number_map


def build_puzzle(word_pool, target_count, seed=None, attempts=10):
    rng = random.Random(seed)
    target_count = min(target_count, len(word_pool))
    best = None
    for _ in range(attempts):
        occupied, placed = _attempt_layout(word_pool, target_count, rng)
        if best is None or len(placed) > len(best[1]):
            best = (occupied, placed)
        if len(placed) >= target_count:
            break
    occupied, placed = best
    occupied, placed, n_rows, n_cols = _normalize(occupied, placed)
    placed, number_map = _assign_numbers(occupied, placed, n_rows, n_cols)
    return {
        "occupied": occupied,
        "placed": placed,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "number_map": number_map,
    }


def build_book(word_pool, puzzle_count, words_per_puzzle, seed=None):
    rng = random.Random(seed)
    puzzles = []
    for i in range(puzzle_count):
        puzzle_seed = rng.randint(0, 10_000_000)
        puzzles.append(build_puzzle(word_pool, words_per_puzzle, seed=puzzle_seed))
    return puzzles


# ---------------------------------------------------------------------------
# On-screen preview (PIL)
# ---------------------------------------------------------------------------
def render_preview_image(puzzle, cell_px=36):
    n_rows, n_cols = puzzle["n_rows"], puzzle["n_cols"]
    occupied = puzzle["occupied"]
    number_map = puzzle["number_map"]
    img = Image.new("RGB", (n_cols * cell_px + 2, n_rows * cell_px + 2), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()

    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) not in occupied:
                continue
            x0, y0 = c * cell_px + 1, r * cell_px + 1
            x1, y1 = x0 + cell_px, y0 + cell_px
            draw.rectangle([x0, y0, x1, y1], outline="black", width=1)
            if (r, c) in number_map:
                draw.text((x0 + 2, y0 + 1), str(number_map[(r, c)]), fill="black", font=font)
    return img


# ---------------------------------------------------------------------------
# PDF building
# ---------------------------------------------------------------------------
MARGIN = 0.5


def _fit_cell_size(n_rows, n_cols, avail_w, avail_h):
    return min(avail_w / n_cols, avail_h / n_rows)


def draw_cover(pdf: FPDF, page_w, page_h, title, photo_bytes):
    pdf.add_page()
    if photo_bytes:
        img = Image.open(BytesIO(photo_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        pdf.image(buf, x=0, y=0, w=page_w, h=page_h)
    else:
        pdf.set_draw_color(0, 0, 0)
        pdf.rect(MARGIN, MARGIN, page_w - 2 * MARGIN, page_h - 2 * MARGIN)
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_xy(MARGIN, page_h / 2 - 0.5)
        pdf.multi_cell(page_w - 2 * MARGIN, 0.5, title, align="C")


def draw_answer_divider(pdf: FPDF, page_w, page_h):
    pdf.add_page()
    pdf.set_draw_color(0, 0, 0)
    box_w, box_h = 4.0, 1.2
    x = (page_w - box_w) / 2
    y = (page_h - box_h) / 2
    pdf.rect(x, y, box_w, box_h)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(x, y + box_h / 2 - 0.2)
    pdf.cell(box_w, 0.4, "ANSWER KEYS", align="C")


def _measure_clue_block_height(pdf, entries, col_w, line_h):
    lines = 0
    for entry in entries:
        wrapped = pdf.multi_cell(col_w - 0.1, line_h, f"{entry['number']}. {entry['clue']}",
                                  dry_run=True, output="LINES")
        lines += len(wrapped)
    return lines * line_h


def _fit_puzzle_layout(pdf, n_rows, n_cols, across, down, avail_w, page_content_h):
    """Try progressively smaller grid/clue sizing until the whole block fits
    the page height, so nothing is ever silently cut off on small trims with
    many words. Returns the largest layout that fits (or the smallest tried,
    as a last-resort fallback)."""
    title_h, gap1, gap2, gap3, bank_h, footer_h, header_h = 0.5, 0.3, 0.25, 0.25, 0.5, 0.35, 0.3
    grid_ratios = [0.60, 0.52, 0.45, 0.38, 0.32]
    clue_settings = [(11, 0.22), (10, 0.20), (9, 0.18), (8, 0.16), (7, 0.145)]

    fallback = None
    for grid_ratio in grid_ratios:
        cell = _fit_cell_size(n_rows, n_cols, avail_w, grid_ratio * page_content_h)
        grid_w = cell * n_cols
        grid_h = cell * n_rows
        col_w = avail_w / 2
        for font_size, line_h in clue_settings:
            pdf.set_font("Helvetica", size=font_size)
            clue_block_h = header_h + max(
                _measure_clue_block_height(pdf, across, col_w, line_h),
                _measure_clue_block_height(pdf, down, col_w, line_h),
            )
            total_h = title_h + gap1 + grid_h + gap2 + clue_block_h + gap3 + bank_h + footer_h
            layout = {
                "cell": cell, "grid_w": grid_w, "grid_h": grid_h, "col_w": col_w,
                "clue_block_h": clue_block_h, "font_size": font_size, "line_h": line_h,
                "total_h": total_h, "title_h": title_h, "gap1": gap1, "gap2": gap2,
                "gap3": gap3, "bank_h": bank_h, "footer_h": footer_h, "header_h": header_h,
            }
            if fallback is None:
                fallback = layout
            if total_h <= page_content_h:
                return layout
    return fallback


def draw_puzzle_page(pdf: FPDF, puzzle, page_w, page_h, puzzle_number):
    pdf.add_page()

    n_rows, n_cols = puzzle["n_rows"], puzzle["n_cols"]
    occupied = puzzle["occupied"]
    number_map = puzzle["number_map"]
    across = sorted([p for p in puzzle["placed"] if p["dir"] == "A"], key=lambda p: p["number"])
    down = sorted([p for p in puzzle["placed"] if p["dir"] == "D"], key=lambda p: p["number"])

    avail_w = page_w - 2 * MARGIN
    page_content_h = page_h - 2 * MARGIN
    layout = _fit_puzzle_layout(pdf, n_rows, n_cols, across, down, avail_w, page_content_h)

    cell = layout["cell"]
    grid_w, grid_h = layout["grid_w"], layout["grid_h"]
    col_w = layout["col_w"]
    line_h = layout["line_h"]
    clue_block_h = layout["clue_block_h"]
    title_h, gap1, gap2, gap3, bank_h, header_h = (
        layout["title_h"], layout["gap1"], layout["gap2"], layout["gap3"],
        layout["bank_h"], layout["header_h"],
    )
    total_h = layout["total_h"]
    top_offset = MARGIN + max(0.0, (page_content_h - total_h) / 2)

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(MARGIN, top_offset)
    pdf.cell(avail_w, title_h, f"PUZZLE {puzzle_number:02d}", align="C")

    grid_top = top_offset + title_h + gap1
    grid_left = MARGIN + (avail_w - grid_w) / 2

    pdf.set_line_width(0.01)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_font("Helvetica", size=max(7, min(11, cell * 20)))
    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) not in occupied:
                continue
            x = grid_left + c * cell
            y = grid_top + r * cell
            pdf.rect(x, y, cell, cell)
            if (r, c) in number_map:
                pdf.set_xy(x + 0.02, y + 0.01)
                pdf.cell(cell - 0.04, 0.12, str(number_map[(r, c)]), align="L")

    clue_top = grid_top + grid_h + gap2

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(MARGIN, clue_top)
    pdf.cell(col_w, header_h, "Across")
    pdf.set_xy(MARGIN + col_w, clue_top)
    pdf.cell(col_w, header_h, "Down")

    pdf.set_font("Helvetica", size=layout["font_size"])
    y = clue_top + header_h
    for entry in across:
        pdf.set_xy(MARGIN, y)
        pdf.multi_cell(col_w - 0.1, line_h, f"{entry['number']}. {entry['clue']}")
        y = pdf.get_y()
    y_down = clue_top + header_h
    for entry in down:
        pdf.set_xy(MARGIN + col_w, y_down)
        pdf.multi_cell(col_w - 0.1, line_h, f"{entry['number']}. {entry['clue']}")
        y_down = pdf.get_y()

    bank_top = clue_top + clue_block_h + gap3
    bank_words = sorted(p["word"] for p in puzzle["placed"])
    bank_text = "   ".join(bank_words)
    pdf.set_draw_color(0, 0, 0)
    pdf.rect(MARGIN, bank_top, avail_w, bank_h)
    pdf.set_font("Helvetica", size=11)
    pdf.set_xy(MARGIN + 0.1, bank_top + 0.15)
    pdf.multi_cell(avail_w - 0.2, 0.2, bank_text, align="C")

    pdf.set_font("Helvetica", size=10)
    pdf.set_xy(MARGIN, page_h - MARGIN - 0.05)
    pdf.cell(avail_w, 0.2, f"{puzzle_number:02d}", align="C")


def draw_answer_grid_page(pdf: FPDF, puzzles, start_index, page_w, page_h):
    pdf.add_page()
    box_w = (page_w - 3 * MARGIN) / 2
    box_h = (page_h - 3 * MARGIN) / 2
    positions = [
        (MARGIN, MARGIN),
        (MARGIN * 2 + box_w, MARGIN),
        (MARGIN, MARGIN * 2 + box_h),
        (MARGIN * 2 + box_w, MARGIN * 2 + box_h),
    ]
    group = puzzles[start_index:start_index + 4]
    pad_x = 0.25
    title_h = 0.35
    header_h = 0.3
    section_gap = 0.12
    font_options = [(16, 0.28), (14, 0.25), (12, 0.22), (11, 0.2), (10, 0.18), (9, 0.16)]

    for idx, puzzle in enumerate(group):
        x, y = positions[idx]
        pdf.rect(x, y, box_w, box_h)

        across = sorted([p for p in puzzle["placed"] if p["dir"] == "A"], key=lambda p: p["number"])
        down = sorted([p for p in puzzle["placed"] if p["dir"] == "D"], key=lambda p: p["number"])

        entry_font, line_h = font_options[-1]
        for candidate_font, candidate_line_h in font_options:
            content_h = (
                title_h + header_h + len(across) * candidate_line_h
                + section_gap + header_h + len(down) * candidate_line_h
            )
            if content_h <= box_h - 0.2:
                entry_font, line_h = candidate_font, candidate_line_h
                break

        content_h = (
            title_h + header_h + len(across) * line_h
            + section_gap + header_h + len(down) * line_h
        )
        content_top = y + max(0.12, (box_h - content_h) / 2)

        pdf.set_font("Helvetica", "B", entry_font + 2)
        pdf.set_xy(x, content_top)
        pdf.cell(box_w, title_h, f"PUZZLE {start_index + idx + 1:02d}", align="C")

        cy = content_top + title_h
        pdf.set_font("Helvetica", "B", entry_font + 1)
        pdf.set_xy(x + pad_x, cy)
        pdf.cell(box_w - 2 * pad_x, header_h, "Across")
        cy += header_h
        pdf.set_font("Helvetica", size=entry_font)
        for entry in across:
            pdf.set_xy(x + pad_x, cy)
            pdf.cell(box_w - 2 * pad_x, line_h, f"{entry['number']}. {entry['word'].title()}")
            cy += line_h

        cy += section_gap
        pdf.set_font("Helvetica", "B", entry_font + 1)
        pdf.set_xy(x + pad_x, cy)
        pdf.cell(box_w - 2 * pad_x, header_h, "Down")
        cy += header_h
        pdf.set_font("Helvetica", size=entry_font)
        for entry in down:
            pdf.set_xy(x + pad_x, cy)
            pdf.cell(box_w - 2 * pad_x, line_h, f"{entry['number']}. {entry['word'].title()}")
            cy += line_h


def build_crossword_pdf(puzzles, page_w, page_h, title, include_cover, photo_bytes, include_answers):
    pdf = FPDF(unit="in", format=(page_w, page_h))
    pdf.set_auto_page_break(False)

    if include_cover:
        draw_cover(pdf, page_w, page_h, title, photo_bytes)

    for i, puzzle in enumerate(puzzles):
        draw_puzzle_page(pdf, puzzle, page_w, page_h, i + 1)

    if include_answers:
        draw_answer_divider(pdf, page_w, page_h)
        for i in range(0, len(puzzles), 4):
            draw_answer_grid_page(pdf, puzzles, i, page_w, page_h)

    out = pdf.output()
    return bytes(out)


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
def main():
    if not check_password():
        st.stop()

    st.title("KDPEasy Crossword Creator")
    st.caption("Sight Words Crossword books, generated instantly - no AI, no prompts, no ChatGPT step.")

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Settings")
        level_choice = st.selectbox("Word level", list(WORD_BANK.keys()) + ["Mixed (Level 1 + 2)"])
        words_per_puzzle = st.slider("Words per puzzle", min_value=5, max_value=12, value=8)
        puzzle_count = st.number_input("Number of puzzles in this book", min_value=1, max_value=50, value=10)
        trim_label = st.selectbox("Page size (KDP trim)", list(TRIM_SIZES.keys()))
        include_answers = st.checkbox("Include answer key section", value=True)
        include_cover = st.checkbox("Include a cover page", value=True)
        photo_bytes = None
        if include_cover:
            uploaded = st.file_uploader("Cover photo (optional - leave empty for a plain text cover)", type=["png", "jpg", "jpeg"])
            if uploaded:
                photo_bytes = uploaded.read()

        book_title = "SIGHT WORDS CROSSWORD PUZZLES"

        generate = st.button("Generate Book", type="primary")

    word_pool = get_word_pool(level_choice)
    max_possible = len(word_pool)
    if words_per_puzzle > max_possible:
        with left:
            st.warning(f"Only {max_possible} words available at this level; using all of them per puzzle.")

    with right:
        st.subheader("Preview")
        preview_puzzle = build_puzzle(word_pool, words_per_puzzle, seed=42)
        preview_img = render_preview_image(preview_puzzle)
        st.image(preview_img, caption="Sample puzzle layout (regenerates with each book)")
        st.write(f"Grid size: {preview_puzzle['n_rows']} x {preview_puzzle['n_cols']}, "
                 f"{len(preview_puzzle['placed'])} words placed")

    if generate:
        page_w, page_h = TRIM_SIZES[trim_label]
        with st.spinner("Generating your book..."):
            puzzles = build_book(word_pool, int(puzzle_count), words_per_puzzle)
            pdf_bytes = build_crossword_pdf(
                puzzles, page_w, page_h, book_title, include_cover, photo_bytes, include_answers
            )
        st.success(f"Book ready - {len(puzzles)} puzzles.")
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="KDPEasy_Sight_Words_Crossword_Book.pdf",
            mime="application/pdf",
        )


if __name__ == "__main__":
    main()

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import os

def draw_box(ax, text, xy, width=0.4, height=0.2, facecolor='#add8e6'):
    box = patches.FancyBboxPatch(
        xy, width, height, boxstyle="round,pad=0.05", 
        edgecolor='black', facecolor=facecolor
    )
    ax.add_patch(box)
    ax.text(xy[0] + width/2, xy[1] + height/2, text, 
            ha='center', va='center', fontsize=10, weight='bold')

def main():
    os.makedirs('docs', exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    draw_box(ax, "User", (0.2, 3.2), facecolor='#d3d3d3')
    draw_box(ax, "React UI\n(Vercel)", (1.2, 3.2), facecolor='#98fb98')
    draw_box(ax, "FastAPI\n(Render)", (1.2, 2.0), width=0.6, height=0.4, facecolor='#ffa07a')
    draw_box(ax, "Planner", (2.8, 3.2), facecolor='#87cefa')
    draw_box(ax, "Executor", (2.8, 2.0), facecolor='#87cefa')
    draw_box(ax, "Reflector", (2.8, 0.8), facecolor='#87cefa')
    draw_box(ax, "LLM", (3.6, 2.0), width=0.3, facecolor='#ffd700')
    draw_box(ax, "Tool Registry", (1.2, 0.5), width=0.6, facecolor='#dda0dd')
    draw_box(ax, "Memory / SQLite", (0.1, 1.5), width=0.5, facecolor='#f0e68c')
    draw_box(ax, "Guardrails", (0.1, 2.5), width=0.5, facecolor='#ffb6c1')
    
    arrows = [
        ((0.6, 3.3), (1.2, 3.3)),
        ((1.4, 3.2), (1.4, 2.4)),
        ((1.5, 2.4), (2.8, 3.3)),
        ((1.8, 2.2), (2.8, 2.2)),
        ((1.5, 2.0), (2.8, 1.0)),
        ((3.2, 3.3), (3.6, 2.2)),
        ((3.2, 2.2), (3.6, 2.1)),
        ((3.2, 1.0), (3.6, 2.0)),
        ((1.5, 2.0), (1.5, 0.7)),
        ((1.2, 2.1), (0.6, 1.6)),
        ((1.2, 2.3), (0.6, 2.6))
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.5))
        
    ax.set_title("StudyPilot Architecture Diagram", fontsize=14, weight='bold')
    plt.tight_layout()
    plt.savefig('docs/schema.png', dpi=150)
    plt.close()
    
    with PdfPages('docs/schema.pdf') as pdf:
        fig, ax = plt.subplots(figsize=(8, 11))
        ax.axis('off')
        ax.text(0.5, 0.6, "StudyPilot Architecture Reference", ha='center', fontsize=24, weight='bold')
        ax.text(0.5, 0.5, "System Design & Schemas", ha='center', fontsize=16)
        pdf.savefig(fig)
        plt.close()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.axis('off')
        draw_box(ax, "User", (0.2, 3.2), facecolor='#d3d3d3')
        draw_box(ax, "Streamlit UI", (1.2, 3.2), facecolor='#98fb98')
        draw_box(ax, "Orchestrator", (1.2, 2.0), width=0.6, height=0.4, facecolor='#ffa07a')
        draw_box(ax, "Planner", (2.8, 3.2), facecolor='#87cefa')
        draw_box(ax, "Executor", (2.8, 2.0), facecolor='#87cefa')
        draw_box(ax, "Reflector", (2.8, 0.8), facecolor='#87cefa')
        draw_box(ax, "LLM", (3.6, 2.0), width=0.3, facecolor='#ffd700')
        draw_box(ax, "Tool Registry", (1.2, 0.5), width=0.6, facecolor='#dda0dd')
        draw_box(ax, "Memory / SQLite", (0.1, 1.5), width=0.5, facecolor='#f0e68c')
        draw_box(ax, "Guardrails", (0.1, 2.5), width=0.5, facecolor='#ffb6c1')
        for start, end in arrows:
            ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.5))
        ax.set_title("Architecture Diagram")
        pdf.savefig(fig)
        plt.close()
        
        fig, ax = plt.subplots(figsize=(8, 11))
        ax.axis('off')
        ax.text(0.5, 0.9, "Tool Reference Table", ha='center', fontsize=18, weight='bold')
        
        table_data = [
            ["Tool Name", "Function"],
            ["web_search", "Search DuckDuckGo"],
            ["wikipedia_summary", "Get topic summary"],
            ["read_webpage", "Read text from URL"],
            ["calculator", "Evaluate math safely"],
            ["weather", "Get current weather"],
            ["save_note", "Save note to SQLite"],
            ["search_notes", "Search notes via LIKE"],
            ["list_notes", "List all notes"],
            ["make_flashcards", "Generate flashcards"],
            ["make_quiz", "Generate MC quiz"],
            ["current_datetime", "Get current time"]
        ]
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.3, 0.6])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        pdf.savefig(fig)
        plt.close()

if __name__ == '__main__':
    main()

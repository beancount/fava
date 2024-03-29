import type { ViewUpdate } from "@codemirror/view";
import { ViewPlugin } from "@codemirror/view";

/**
 * This CodeMirror view plugin creates a ruler at (before) the given column.
 */
export const rulerPlugin = (
  column: number,
): ViewPlugin<{
  update(update: ViewUpdate): void;
  destroy(): void;
}> =>
  ViewPlugin.define((view) => {
    const ruler = view.dom.appendChild(document.createElement("div"));
    ruler.style.position = "absolute";
    ruler.style.borderRight = "1px dotted black";
    ruler.style.height = "100%";
    ruler.style.opacity = "0.5";
    ruler.style.pointerEvents = "none";

    const updatePosition = () => {
      const firstLine = view.contentDOM.querySelector(".cm-line");
      if (firstLine) {
        const { paddingLeft } = getComputedStyle(firstLine);
        const domRect = view.dom.getBoundingClientRect();
        const contentDOMRect = view.contentDOM.getBoundingClientRect();
        // We need to add the width of the gutter (line numbers etc.) since
        // our ruler is positioned absolutely within the whole editor.
        const gutterWidth = contentDOMRect.x - domRect.x;
        const offset = column * view.defaultCharacterWidth + gutterWidth;
        ruler.style.width = paddingLeft;
        ruler.style.left = `${offset.toString()}px`;
      }
    };

    view.requestMeasure({ read: updatePosition });

    return {
      update(update) {
        if (update.viewportChanged || update.geometryChanged) {
          view.requestMeasure({ read: updatePosition });
        }
      },

      destroy() {
        ruler.remove();
      },
    };
  });

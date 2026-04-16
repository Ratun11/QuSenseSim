window.DragDropManager = (() => {
    function makeSensorDraggable(element, workspace, onMove, onSelect, onEnd) {
        let dragging = false;
        let moved = false;
        let startX = 0;
        let startY = 0;
        let originLeft = 0;
        let originTop = 0;

        const onPointerMove = (event) => {
            if (!dragging) return;

            const dx = event.clientX - startX;
            const dy = event.clientY - startY;
            if (Math.abs(dx) > 2 || Math.abs(dy) > 2) moved = true;

            const maxX = workspace.clientWidth - element.offsetWidth;
            const maxY = workspace.clientHeight - element.offsetHeight;
            const nextLeft = Math.min(Math.max(0, originLeft + dx), maxX);
            const nextTop = Math.min(Math.max(0, originTop + dy), maxY);

            element.style.left = `${nextLeft}px`;
            element.style.top = `${nextTop}px`;

            if (typeof onMove === "function") {
                onMove(nextLeft, nextTop);
            }
        };

        const stopDragging = () => {
            if (!dragging) return;
            dragging = false;
            element.classList.remove("dragging");
            window.removeEventListener("pointermove", onPointerMove);
            window.removeEventListener("pointerup", stopDragging);

            if (moved && typeof onEnd === "function") {
                onEnd();
            }
            setTimeout(() => { moved = false; }, 0);
        };

        element.addEventListener("pointerdown", (event) => {
            event.preventDefault();
            dragging = true;
            moved = false;
            element.classList.add("dragging");
            startX = event.clientX;
            startY = event.clientY;
            originLeft = parseFloat(element.style.left || "0");
            originTop = parseFloat(element.style.top || "0");

            if (typeof onSelect === "function") {
                onSelect();
            }

            window.addEventListener("pointermove", onPointerMove);
            window.addEventListener("pointerup", stopDragging);
        });
    }

    return { makeSensorDraggable };
})();

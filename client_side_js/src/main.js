import { Crepe } from "@milkdown/crepe";
import "@milkdown/crepe/theme/common/style.css";
import "@milkdown/crepe/theme/frame.css";

window.initMilkdownCrepe = async function(domId, defaultValue = "") {
    const crepe = new Crepe({
        root: document.getElementById(domId),
        defaultValue: defaultValue,
    });
    await crepe.create();
    return crepe;
};

// If headings still appear in the UI, add this CSS to hide them:
// .milkdown .slash-menu [data-type="heading"] { display: none !important; }
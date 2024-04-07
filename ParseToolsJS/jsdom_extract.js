const jsdom = require("jsdom");
const { JSDOM } = jsdom;

function extractRenderedText(htmlContent) {
    const dom = new JSDOM(htmlContent);
    const document = dom.window.document;

    // 1. Remove Unnecessary Elements
    document.querySelectorAll("script, style, noscript, nav, header, footer").forEach(el => el.remove());    

    // 2. Get All Text Nodes
    function getAllTextNodes(node) {
        let textNodes = [];
        if (node.nodeType === document.Node.TEXT_NODE) { // Access 'Node' through 'document'
            textNodes.push(node.textContent.trim());
        } else {
            for (const child of node.childNodes) {
                textNodes = textNodes.concat(getAllTextNodes(child));
            }
        }
        return textNodes;
    }

    const allTextNodes = getAllTextNodes(document.body);

    // 3. Join Text Nodes (optional - adjust as needed)
    const renderedText = allTextNodes.join(" "); 

    return renderedText;
}

// Read HTML from the file (passed as an argument)
const fs = require('fs');
const htmlFile = process.argv[2];
const htmlContent = fs.readFileSync(htmlFile, 'utf-8');

const renderedText = extractRenderedText(htmlContent);
console.log(renderedText);

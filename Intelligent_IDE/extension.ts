async function generateCode(prompt: string) {
    const response = await fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
    });

    const data = await response.json();
    if (data.code) {
        insertCodeToEditor(data.code);
    }
}

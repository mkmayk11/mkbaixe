async function iniciarDownload() {
    const url = document.getElementById("url").value.trim();
    const formato = document.getElementById("formato").value;
    const qualidade = document.getElementById("qualidade").value;
    const nome = document.getElementById("nome").value.trim();

    document.getElementById("status").innerText = "Baixando... aguarde ⏳";
    document.getElementById("link").innerText = "";

    const resposta = await fetch("/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, formato, qualidade, nome })
    });

    const data = await resposta.json();

    if (data.status === "ok") {
        document.getElementById("status").innerText = "✅ " + data.msg;
        document.getElementById("link").innerHTML = `<a href="/downloads/${data.arquivo}" target="_blank">Clique aqui para baixar</a>`;
    } else {
        document.getElementById("status").innerText = "❌ Erro: " + data.msg;
    }
}

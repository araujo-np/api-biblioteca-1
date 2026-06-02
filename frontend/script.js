const API = "http://127.0.0.1:8000";

let livrosEncontrados = [];

const containerResultados = document.getElementById("resultadosBusca");
const inputBusca = document.getElementById("inputBusca");
const btnBusca = document.getElementById("btnBusca");

// Busca livros na API preservando alterações locais
async function carregarLivros() {
    try {
        const resposta = await fetch(`${API}/livros`);

        if (!resposta.ok) {
            throw new Error("Erro ao buscar livros");
        }

        const dados = await resposta.json();

        // MAPEIA OS DADOS: Se o livro já foi reservado localmente, mantém como indisponível
        livrosEncontrados = dados.map(novoLivro => {
            const livroLocal = livrosEncontrados.find(l => l.id === novoLivro.id);
            if (livroLocal && livroLocal.disponivel === false) {
                return { ...novoLivro, disponivel: false };
            }
            return novoLivro;
        });

        // Se o usuário estiver digitando uma busca, mantém o filtro visual ativo
        const termo = inputBusca.value.trim().toLowerCase();
        if (termo !== "") {
            realizarBusca();
        } else {
            exibirLivros(livrosEncontrados);
        }

    } catch (erro) {
        console.error("Erro:", erro);
        containerResultados.innerHTML = `
            <p>Não foi possível carregar os livros.</p>
        `;
    }
}
// Exibe os livros na tela
function exibirLivros(listaDeLivros) {
    containerResultados.innerHTML = "";

    if (listaDeLivros.length === 0) {
        containerResultados.innerHTML =
            "<p>Nenhum livro encontrado.</p>";
        return;
    }

    listaDeLivros.forEach((livro) => {

        const card = document.createElement("div");
        card.classList.add("card-livro");

        const img = document.createElement("img");
        img.src = livro.imagem || "https://via.placeholder.com/150";
        img.alt = livro.titulo;

        const titulo = document.createElement("h3");
        titulo.textContent = livro.titulo;

        const autor = document.createElement("p");
        autor.textContent = `Autor: ${livro.autor}`;

        const status = document.createElement("p");
        status.textContent =
            livro.disponivel ? "Disponível" : "Indisponível";

        status.classList.add(
            livro.disponivel
                ? "disponivel"
                : "indisponivel"
        );

        const botao = document.createElement("button");

        if (livro.disponivel) {
            botao.textContent = "Reservar";
        } else {
            botao.textContent = "Indisponível";
            botao.disabled = true;
        }

        botao.addEventListener("click", () => {

            livro.disponivel = false;

            status.textContent = "Indisponível";

            status.classList.remove("disponivel");
            status.classList.add("indisponivel");

            botao.textContent = "Reservado!";
            botao.disabled = true;
        });

        card.appendChild(img);
        card.appendChild(titulo);
        card.appendChild(autor);
        card.appendChild(status);
        card.appendChild(botao);

        containerResultados.appendChild(card);
    });
}

// Pesquisa livros
function realizarBusca() {

    const termo = inputBusca.value
        .trim()
        .toLowerCase();

    if (termo === "") {
        exibirLivros(livrosEncontrados);
        return;
    }

    const livrosFiltrados =
        livrosEncontrados.filter((livro) =>
            livro.titulo.toLowerCase().includes(termo) ||
            livro.autor.toLowerCase().includes(termo)
        );

    exibirLivros(livrosFiltrados);
}

// Eventos
btnBusca.addEventListener("click", realizarBusca);

inputBusca.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        realizarBusca();
    }
});

// Inicialização
carregarLivros();

// Atualiza automaticamente a cada 3 segundos
setInterval(carregarLivros, 3000);
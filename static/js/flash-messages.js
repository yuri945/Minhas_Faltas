document.addEventListener("DOMContentLoaded", () => {

    const mensagens = document.querySelectorAll(".mensagem");

    mensagens.forEach((mensagem) => {

        setTimeout(() => {
            mensagem.classList.add("sumindo");

            setTimeout(() => {
                mensagem.remove();
            }, 300);

        }, 3000);

    });

});
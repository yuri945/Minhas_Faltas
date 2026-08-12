let deferredPrompt = null;

const installButton = document.getElementById("installApp");

if (installButton) {

    // Chrome/Edge/Android informa que o PWA pode ser instalado
    window.addEventListener("beforeinstallprompt", (event) => {

        // Impede o navegador de mostrar o prompt automaticamente
        event.preventDefault();

        // Guarda o evento para usarmos quando o usuário clicar
        deferredPrompt = event;

        // Libera o botão.
        // O CSS garante que ele só aparecerá no celular.
        installButton.classList.add("disponivel");
    });


    // Usuário clicou em "Instalar app"
    installButton.addEventListener("click", async () => {

        if (!deferredPrompt) {
            return;
        }

        // Abre a instalação nativa do navegador
        deferredPrompt.prompt();

        // Aguarda o usuário aceitar ou cancelar
        const { outcome } = await deferredPrompt.userChoice;

        console.log(
            `Resultado da instalação do PWA: ${outcome}`
        );

        // O evento só pode ser utilizado uma vez
        deferredPrompt = null;

        // Esconde novamente o botão
        installButton.classList.remove("disponivel");
    });


    // Executado quando o aplicativo terminar de ser instalado
    window.addEventListener("appinstalled", () => {

        deferredPrompt = null;

        installButton.classList.remove("disponivel");

        console.log("Minhas Faltas instalado com sucesso.");
    });
}
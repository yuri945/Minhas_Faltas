let deferredPrompt = null;

const installButton = document.getElementById("installApp");


const isIOS =
    /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (
        navigator.platform === "MacIntel" &&
        navigator.maxTouchPoints > 1
    );


const isStandalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;




if (installButton && isIOS && !isStandalone) {

    installButton.classList.add("disponivel");

    installButton.addEventListener("click", () => {

        alert(
            "Para instalar o Minhas Faltas no iPhone:\n\n" +
            "1. Toque no botão Compartilhar do Safari.\n" +
            "2. Escolha \"Adicionar à Tela de Início\".\n" +
            "3. Toque em \"Adicionar\"."
        );

    });

}




window.addEventListener("beforeinstallprompt", (event) => {

    event.preventDefault();

    deferredPrompt = event;

    if (installButton && !isStandalone) {
        installButton.classList.add("disponivel");
    }

});


if (installButton) {

    installButton.addEventListener("click", async () => {

        // No iPhone este bloco não executa
        if (isIOS) {
            return;
        }

        if (!deferredPrompt) {
            return;
        }

        deferredPrompt.prompt();

        const { outcome } =
            await deferredPrompt.userChoice;

        console.log(
            `Resultado da instalação: ${outcome}`
        );

        deferredPrompt = null;

        installButton.classList.remove("disponivel");

    });

}



window.addEventListener("appinstalled", () => {

    deferredPrompt = null;

    if (installButton) {
        installButton.classList.remove("disponivel");
    }

});
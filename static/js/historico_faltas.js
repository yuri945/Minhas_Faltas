document.addEventListener("DOMContentLoaded", function () {
    const dadosFaltas = document.getElementById("dados-faltas");
    const titulo = document.getElementById("titulo-calendario");
    const grade = document.getElementById("grade-calendario");
    const botaoAnterior = document.getElementById("mes-anterior");
    const botaoProximo = document.getElementById("proximo-mes");

    if (
        !dadosFaltas ||
        !titulo ||
        !grade ||
        !botaoAnterior ||
        !botaoProximo
    ) {
        return;
    }

    let faltas = [];

    try {
        const conteudo = dadosFaltas.textContent.trim();

        faltas = JSON.parse(conteudo || "[]");
    } catch (erro) {
        console.error("Erro ao carregar os dados das faltas:", erro);
        faltas = [];
    }

    const faltasPorData = new Map();

    faltas.forEach(function (falta) {
        const data = falta.data;
        const quantidade = Number(falta.quantidade) || 0;
        const quantidadeAtual = faltasPorData.get(data) || 0;

        faltasPorData.set(
            data,
            quantidadeAtual + quantidade
        );
    });

    const nomesMeses = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro"
    ];

    let dataExibida = obterDataInicial();

    function obterDataInicial() {
        if (faltas.length === 0) {
            const hoje = new Date();

            return new Date(
                hoje.getFullYear(),
                hoje.getMonth(),
                1
            );
        }

        const datasOrdenadas = faltas
            .map(function (falta) {
                return falta.data;
            })
            .sort();

        const ultimaData = datasOrdenadas[datasOrdenadas.length - 1];
        const partes = ultimaData.split("-").map(Number);

        return new Date(
            partes[0],
            partes[1] - 1,
            1
        );
    }

    function formatarChaveData(ano, mes, dia) {
        const mesFormatado = String(mes + 1).padStart(2, "0");
        const diaFormatado = String(dia).padStart(2, "0");

        return `${ano}-${mesFormatado}-${diaFormatado}`;
    }

    function criarCelulaVazia() {
        const elemento = document.createElement("span");

        elemento.className =
            "dia-calendario dia-calendario-vazio";

        elemento.setAttribute("aria-hidden", "true");

        return elemento;
    }

    function criarCelulaDia(ano, mes, dia) {
        const chave = formatarChaveData(ano, mes, dia);
        const quantidade = faltasPorData.get(chave) || 0;
        const elemento = document.createElement("div");
        const numeroDia = document.createElement("span");

        elemento.className = "dia-calendario";
        numeroDia.textContent = dia;

        elemento.appendChild(numeroDia);

        if (quantidade > 0) {
            elemento.classList.add("dia-com-falta");

            elemento.setAttribute(
                "aria-label",
                `${dia} de ${nomesMeses[mes]}: ${quantidade} falta(s)`
            );

            const marcador = document.createElement("small");

            marcador.textContent = quantidade;
            marcador.title = `${quantidade} falta(s)`;

            elemento.appendChild(marcador);
        } else {
            elemento.setAttribute(
                "aria-label",
                `${dia} de ${nomesMeses[mes]}: sem faltas`
            );
        }

        return elemento;
    }

    function renderizarCalendario() {
        const ano = dataExibida.getFullYear();
        const mes = dataExibida.getMonth();

        const primeiroDiaSemana = new Date(
            ano,
            mes,
            1
        ).getDay();

        const totalDias = new Date(
            ano,
            mes + 1,
            0
        ).getDate();

        titulo.textContent = `${nomesMeses[mes]} de ${ano}`;
        grade.innerHTML = "";

        for (
            let indice = 0;
            indice < primeiroDiaSemana;
            indice += 1
        ) {
            grade.appendChild(criarCelulaVazia());
        }

        for (
            let dia = 1;
            dia <= totalDias;
            dia += 1
        ) {
            grade.appendChild(
                criarCelulaDia(ano, mes, dia)
            );
        }

        completarUltimaSemana(
            primeiroDiaSemana,
            totalDias
        );
    }

    function completarUltimaSemana(
        primeiroDiaSemana,
        totalDias
    ) {
        const totalCelulas =
            primeiroDiaSemana + totalDias;

        const restante = totalCelulas % 7;

        if (restante === 0) {
            return;
        }

        const quantidadeVazias = 7 - restante;

        for (
            let indice = 0;
            indice < quantidadeVazias;
            indice += 1
        ) {
            grade.appendChild(criarCelulaVazia());
        }
    }

    botaoAnterior.addEventListener(
        "click",
        function () {
            dataExibida = new Date(
                dataExibida.getFullYear(),
                dataExibida.getMonth() - 1,
                1
            );

            renderizarCalendario();
        }
    );

    botaoProximo.addEventListener(
        "click",
        function () {
            dataExibida = new Date(
                dataExibida.getFullYear(),
                dataExibida.getMonth() + 1,
                1
            );

            renderizarCalendario();
        }
    );

    renderizarCalendario();
});
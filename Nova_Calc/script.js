// script.js

// Ottieni il riferimento all'elemento del display
const display = document.getElementById('display');

// Flag per gestire l'input dopo un calcolo/risoluzione
let ultimaOperazioneÈCalcolo = false;

/**
 * Aggiunge un valore al display.
 * Gestisce il reset del display se l'ultima operazione è stata un calcolo
 * o se il display mostra "0" e si preme un numero.
 * @param {string} valore - Il valore da aggiungere al display.
 */
function aggiungi(valore) {
  if (ultimaOperazioneÈCalcolo && !isNaN(valore) && valore !== '.') {
    // Se l'ultima operazione era un calcolo e si digita un numero (non un operatore o punto)
    // resetta il display con il nuovo valore.
    display.value = valore;
  } else if (display.value === '0' && !isNaN(valore) && valore !== '.') {
    // Se il display è "0" e si digita un numero (non un operatore o punto),
    // sostituisce "0" con il numero.
    display.value = valore;
  } else {
    // Aggiunge il valore al display.
    display.value += valore;
  }
  // Resetta il flag dopo ogni aggiunta.
  ultimaOperazioneÈCalcolo = false;
}

/**
 * Esegue il calcolo dell'espressione presente nel display.
 * Utilizza la libreria math.js.
 */
function calcola() {
  try {
    // Sostituisce la virgola con il punto per compatibilità con math.js
    const espressione = display.value.replace(/,/g, '.');
    const risultato = math.evaluate(espressione);
    // Visualizza il risultato, riconvertendo il punto in virgola per l'output
    display.value = risultato.toString().replace('.', ',');
    // Imposta il flag per indicare che è stato eseguito un calcolo.
    ultimaOperazioneÈCalcolo = true;
  } catch (e) {
    // In caso di errore nel calcolo, mostra "Errore Calcolo".
    display.value = 'Errore Calcolo';
    ultimaOperazioneÈCalcolo = true;
  }
}

/**
 * Pulisce completamente il display.
 */
function pulisci() {
  display.value = '';
  ultimaOperazioneÈCalcolo = false;
}

/**
 * Cancella l'ultimo carattere dal display.
 */
function cancellaUltimo() {
    display.value = display.value.slice(0, -1);
    ultimaOperazioneÈCalcolo = false;
}

/**
 * Risolve un'equazione utilizzando la libreria Nerdamer.js.
 * Cerca di determinare la variabile (x, y, z) e gestisce alcuni casi di soluzione.
 */
async function risolviEquazione() {
    // Prepara l'equazione, sostituendo le virgole con i punti.
    let equazione = display.value.replace(/,/g, '.'); 
    let variabile = 'x'; // Variabile predefinita

    // Semplice euristica per rilevare la variabile se non è 'x'
    if (equazione.includes('y') && !equazione.includes('x')) {
        variabile = 'y';
    } else if (equazione.includes('z') && !equazione.includes('x') && !equazione.includes('y')) {
        variabile = 'z';
    }

    display.value = 'Risoluzione...'; // Messaggio di caricamento

    try {
        // Usa nerdamer.solve per ottenere le soluzioni.
        const soluzioni = nerdamer.solve(equazione, variabile);

        if (soluzioni && soluzioni.length > 0) {
            let risultatoSoluzioni = [];
            soluzioni.forEach(sol => {
                // Formatta ogni soluzione, riconvertendo il punto in virgola.
                risultatoSoluzioni.push(sol.toString().replace('.', ','));
            });
            display.value = `${variabile} = ${risultatoSoluzioni.join(', ')}`;
        } else {
            // Gestisce i casi di "infinite soluzioni" o "nessuna soluzione"
            // Se l'equazione contiene '=', tenta una valutazione simbolica per coerenza.
            if (equazione.includes('=')) {
                const [lhs, rhs] = equazione.split('='); // Parte sinistra e destra dell'equazione
                try {
                    // Semplifica simbolicamente entrambe le parti
                    const lhsSimplified = nerdamer(lhs).text();
                    const rhsSimplified = nerdamer(rhs).text();

                    if (lhsSimplified === rhsSimplified) {
                        display.value = 'Infinite soluzioni';
                    } else {
                        display.value = 'Nessuna soluzione';
                    }
                } catch {
                     // Fallback se la semplificazione simbolica fallisce
                     display.value = 'Nessuna soluzione'; 
                }
            } else {
                 display.value = 'Nessuna soluzione'; // Non è un'equazione valida se non ha '='
            }
        }
    } catch (e) {
        // Cattura errori dalla libreria Nerdamer o problemi di parsing.
        console.error("Errore durante la risoluzione dell'equazione con Nerdamer:", e);
        display.value = 'Errore Eq.';
    }
    ultimaOperazioneÈCalcolo = true;
}="display" placeh
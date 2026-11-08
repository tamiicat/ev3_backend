(function () {
    'use strict';

    var boton = document.getElementById('btn-reservar');
    var aviso = document.getElementById('aviso-seleccion');
    if (!boton || !aviso) return;           
    // Itinerario: de 3 a 5 (checkbox) - Hotel y vuelo: 1 (radio).
    var grupos = [
        { etiqueta: 'actividad(es)', radio: false,
        checks: document.querySelectorAll('.chk-actividad'),
        contador: document.getElementById('contador-actividades'), minDeseado: 3, max: 5 },
        { etiqueta: 'hotel', radio: true,
        checks: document.querySelectorAll('.chk-hotel'),
        contador: document.getElementById('contador-hoteles'), minDeseado: 1, max: 1 },
        { etiqueta: 'vuelo', radio: true,
        checks: document.querySelectorAll('.chk-vuelo'),
        contador: document.getElementById('contador-vuelos'), minDeseado: 1, max: 1 }
    ].filter(function (g) { return g.checks.length > 0; });  

    if (!grupos.length) return;

    function actualizar() {
        var valido = true, pendientes = [], libres = [];

        grupos.forEach(function (g) {
            // si hay menos opciones que el mínimo, el mínimo es el total disponible
            var min = Math.min(g.minDeseado, g.checks.length);
            var marcadas = 0;
            g.checks.forEach(function (c) { if (c.checked) marcadas++; });

            // en checkbox, al llegar al máximo se bloquean las demás (los radio permiten solo una)
            if (!g.radio) {
                g.checks.forEach(function (c) { c.disabled = !c.checked && marcadas >= g.max; });
            }

            if (g.contador) g.contador.textContent = marcadas + ' / ' + g.max;

            if (marcadas < min) {
                valido = false;
                pendientes.push((min - marcadas) + ' ' + g.etiqueta + (g.radio ? '' : ' más'));
            } else if (marcadas < g.max) {
                libres.push((g.max - marcadas) + ' ' + g.etiqueta);
            }
        });

        boton.disabled = !valido;

        if (!valido) {
            aviso.textContent = 'Selecciona ' + pendientes.join(' y ') + ' para reservar.';
        } else if (libres.length) {
            aviso.textContent = 'Aún puedes añadir hasta ' + libres.join(' y ') + '.';
        } else {
            aviso.textContent = 'Tu selección está completa.';
        }
    }

    grupos.forEach(function (g) {
        g.checks.forEach(function (c) { c.addEventListener('change', actualizar); });
    });
    actualizar();
})();
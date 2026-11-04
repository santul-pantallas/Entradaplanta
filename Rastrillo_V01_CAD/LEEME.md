# Rastrillo para hojas V01

Concepto original inspirado en la arquitectura de rastrillos de las patentes US3724188A, US4831815A y USD625571S1. No es una replica dimensional de Truper. No incorpora el CAD de GrabCAD descartado.

## Archivos
- Rastrillo_V01.step: cabeza sin mango, un solido B-Rep, unidades milimetros. Para importar en SolidWorks y otros CAD.
- Rastrillo_V01.stl: malla auxiliar de visualizacion/prototipo; no sustituye el STEP. Importar en milimetros.
- Vista_CAD_V01.png: vistas renderizadas de la geometria real.
- Verificacion_V01.json: dimensiones reales de la envolvente, volumen y comprobaciones.
- generar_rastrillo.py: fuente parametrica en Python/CadQuery. El STEP no contiene un arbol de operaciones nativo de SolidWorks.

## Dimensiones propuestas
Envolvente nominal 600 x 430 mm, 26 dientes. Panel 2.8 mm. Dientes 8 mm de ancho x 3 mm de espesor base. Nervaduras 1.5 mm de espesor con altura variable. Puente transversal de 9 mm en direccion radial. Curvatura de las puntas: radio de eje 20 mm, giro 70 grados, tramo terminal recto 16 mm.

Mango: alojamiento cilindrico nominal de diametro 25.4 mm y profundidad util 90 mm, pared radial 3 mm. Perforacion de fijacion diametro 4.5 mm a 35 mm de la boca. El mango no esta incluido. Alojamiento sin conicidad ni tolerancia de ajuste definida.

Las dimensiones exactas de la envolvente se registran en Verificacion_V01.json. El render conceptual previo no era un modelo geometrico exacto; esta version fija una geometria reproducible.

## Estado y limitaciones
Prototipo geometrico para revision, NO liberado para fabricar un molde. No se ha simulado carga, fatiga, fluencia, llenado ni alabeo. Polipropileno previsto; grado, UV, reciclado y contraccion por definir. La masa indicada usa una densidad asumida de 0.90 g/cm3.

Quedan pendientes angulos de salida, radios completos de raiz y uniones, linea de particion, nucleo del alojamiento, expulsion, ventilacion, punto de inyeccion y tolerancias. Las pequenas suavizaciones de punta no equivalen a un redondeado completo de todas las aristas. No se garantiza apertura simple de molde en dos placas.

Para pruebas funcionales, un prototipo FDM no reproduce automaticamente la respuesta de PP inyectado.

## Reproducir
Python 3.12 y CadQuery 2.8.0. Ejecutar generar_rastrillo.py. Para la imagen ejecutar renderizar.py con numpy y matplotlib. Las variables al inicio del script controlan numero de dientes y espesores; el resto de parametros geometricos estan documentados en el codigo.

## Referencias
- https://patents.google.com/patent/US3724188A/en
- https://patents.google.com/patent/US4831815A/en
- https://patents.google.com/patent/USD625571S1/en
- https://www.protolabs.com/resources/design-tips/improving-part-design-with-uniform-wall-thickness/

La guia de Protolabs orienta el espesor de paredes y nervaduras; no valida por si sola la funcion del rastrillo.

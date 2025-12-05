Il seguente progetto ha l'obiettivo diun clustering delle isole del mondo sulla base di variabili  natura socioeconomica e risorse naturali. L'obiettivo del progetto è quello di suddividere le isole in cluster basati sulle caratteristiche per i percorsi di transizione energetica. Le isole degli stessi clusters avranno, presumibilmente, caratteristiche simili e, in linea di massima, dovranno seguire strategie simili nel processo di transizione.

Il progetto è organizzato in tre cartelle principali:

-src_data

-exploratory_data_analisys

-clustering

In qualunque cartella siano presenti cartelle o script numerati significa che i rogrammi devono essere eseguiti in ordine sequenziale in quanto i risultati degli script precedenti sono necessari per l'esecuzione di quelli successivi.

# Cartella src_data

In questa cartella sono presenti gli script per definire le isole oggetto dello studio e raccogliere i dati necessari.
Il primo script è necessario per scaricare i file necessari agli script successivi.
Le isole sono raccolte e filtrate in base a criteri di dimensioni e distanza dalla terraferma e sono calcolati dei proxy relativi alle seguenti caratteristiche:

-popolazione.tif

-potenziale solare e sua variabilità durante l'anno

-potenziale eolico onshore e offshore e sua variabilità durante l'anno

-superficie urbana

-elevazione massima

-temperatura media, precipitazioni, heating days, cooling days

-GDP e consumi elettrici del 2019

-EVI

-potenziale geotermico

-potenziale idroelettrico

-stima della superficie agibile per la realizzazione di impianti a energia rinnovabile (RES)

# Cartella exploratory_data_analisys

In questa cartella sono presenti gli script per l'esplorazione dei dati e le operazioni di normalizzazione propedeutiche al processo di clustering. Le cartelle '1-raw', '2-dimensions_reduction' e '3-normalized' dovrebbero essere eseguite in ordine sequenziale e dopo la cartella 'src_data'. Poiché sono stati già caricati i dataframe creati nei diversi step è possibile l'esecuzione in ordine casuale degli script. Sono stati caricati anche tutti i grafici realizzati, consultabili senza eseguire gli script.

# Cartella clustering

In questa cartella sono presenti gli script di esecuzione di tre metodologie di clustering separate e di un'analisi dei risultati mediante la realizzazione di grafici e tabelle riassuntive. Anche in questo caso sono stati caricati anche tutti i grafici realizzati, consultabili senza eseguire gli script.

La cartella 'multi_algo' tenta diversi algortimi tradizionali selezionando i migiori in base a diverse metriche di valutazione. I risultati non sono ritenuti soddisfacenti.

La cartella 'constrained' tenta diversi algoritmi di clustering vincolato. Anche in questo caso i risultati non sono ritenuti soddisfacenti. Alcuni algoritmi non hanno raggiunto una soluzione a causa dell'elevato carico computazionale.

La cartella 'pipeline_finale' propone un approccio in due step suddividendo le variabili di interesse tra le due fasi vusto il loro numero elevato.
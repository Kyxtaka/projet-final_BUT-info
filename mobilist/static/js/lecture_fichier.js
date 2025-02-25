document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.querySelector("#form_justif + input");
    
    fileInput.addEventListener("change", function(event) {
        const file = event.target.files[0];
        console.log(file);
        if (file) {
            const reader = new FileReader();

            reader.onload = function(e) {
                try {
                    const data = JSON.parse(e.target); 

                    document.querySelector("#logement-select").value = data.logement || "";
                    document.querySelector("#form_nom + input").value = data.nom_bien || "";
                    document.querySelector("#form_cat + input").value = data.categorie_bien || "";
                    document.querySelector("#form_type + input").value = data.type_bien || "";
                    document.querySelector("#piece-select").value = data.piece_bien || "";
                    document.querySelector("#form_prix + input").value = data.prix_bien || "";
                    document.querySelector("#form_date + input").value = data.date_bien || "";
                    document.querySelector("#form_desc + textarea").value = data.description_bien || "";

                } catch (error) {
                    console.error("Erreur lors de la lecture du fichier : ", error);
                }
            };

            reader.readAsText(file);
        }
    });
});
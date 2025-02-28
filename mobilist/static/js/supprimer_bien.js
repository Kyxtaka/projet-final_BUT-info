
    class Bien {
        id;
        name;
        prix;
        constructor(name, prix, id) {
            this.id = `bien-${id}`;
            this.name = name;
            this.prix = prix;
        }
    }
    
   

    document.addEventListener("DOMContentLoaded", function() {
        const { BehaviorSubject } = rxjs; // import de rxjs apres avoir load le script dans le html car on utilise pas node et Typescript
        const arraybiens = new BehaviorSubject([]);
        const $arrybiens = arraybiens.asObservable();
        const bienFormButton = document.getElementById('supp-bien-btn');
        const bienTable = document.getElementById('bien-list');
    
        document.querySelectorAll(".btn").forEach(button => {
            button.addEventListener("click", function(event) {
                let idBien = this.id;
                console.log("Bouton cliqué avec ID:", idBien);
                if(this.innerText === "Supprimer") {
                    event.preventDefault();
                    let bienName = document.getElementById(`nomBien${idBien}`).textContent;
                    let bienPrix = parseFloat(document.getElementById(`prixBien${idBien}`).textContent);
                
                    console.log("bienName", bienName);
                    console.log("bienPrix", bienPrix);
                
                    let bien = new Bien(bienName, bienPrix, idBien);
                
                    arraybiens.next([...arraybiens.getValue(), bien]);
                    console.log("Updated biens array:", arraybiens.getValue());
                
                    this.innerText = "Annuler";
                } else if(this.innerText === "Annuler") {
                        event.preventDefault();
                        const updatedbiens = arraybiens.getValue().filter(bien => bien.id !== `bien-${idBien}`);
                        arraybiens.next(updatedbiens);
                        
                        console.log("Updated biens array:", arraybiens.getValue());
                        this.innerText = "Supprimer";
                } else if(this.innerText === "Confirmer") {
                    deleteBiens(); 
                }
                
            });
    
            document.getElementById("confirmersupp").addEventListener("click", deleteBiens); 
    
            $arrybiens.subscribe({
                next: (reponse) => {
                    bienPrixSupprimer = 0;
                    reponse.forEach(element => {
                        bienPrixSupprimer += element.prix;
                    });
                    document.getElementById("total").textContent = bienPrixSupprimer;
                },
                error: (error) => {
                    console.error(error);
                },
            });

            function deleteBiens() {
                fetch("{{ url_for('biens.mesBiens')}}" + "?logement=" + "{{ logement_id }}", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(arraybiens.getValue()),
                }).then(response => {
                    if (response.ok) {
                        console.log("biens supprimés");
                        arraybiens.next([]);
                    } else {
                        console.error("Erreur lors de la suppression des biens");
                    }
                }).catch(error => {
                    console.error("Erreur lors de la suppression des biens", error);
                });
            }
        });
    });

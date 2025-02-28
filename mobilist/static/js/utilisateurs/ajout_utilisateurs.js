
class Utilisateur{
    id;
    nom;
    prenom;
    mail;
    constructor(id, nom, prenom, mail) {
        this.id = `utilisateur-${id}`;
        this.nom = nom;
        this.prenom = prenom;
        this.mail = mail;
    }

    toString() {
        console.log(this.nom, this.prenom, this.mail);
        return this.nom + " " + this.prenom + " " + this.mail;
    }
}


document.addEventListener("DOMContentLoaded", function() {
    const { BehaviorSubject } = rxjs; // import de rxjs apres avoir load le script dans le html car on utilise pas node et Typescript

    let elementId = 0;
    const arrayUtilisateurs = new BehaviorSubject([]);
    const $arryUtilisateurs = arrayUtilisateurs.asObservable();

    const utilisateurForm = document.getElementById("add-utilisateur-form");
    const formUtilisateursArray = document.getElementById("form-utilisateurs-array");
    utilisateurForm.addEventListener("submit", function(event) {
        event.preventDefault();
        console.log("arrayUtilisateur s JSON", JSON.stringify(arrayUtilisateurs.getValue()));
        document.getElementById("utilisateurs-array").value = JSON.stringify(arrayUtilisateurs.getValue());

        document.getElementById("")
        console.log("form submitted");
        utilisateurForm.submit();
    });

    const utilisateurFormButton = document.getElementById('add-utilisateur-btn');
    const utilisateurTable = document.getElementById('utilisateur-list');

    utilisateurFormButton.addEventListener("click", function(event) {
        console.log("button clicked");

        event.preventDefault();
        let utilisateurName = document.getElementById('edit-utilisateur-name-input').value;
        let utilisateurDescription = document.getElementById('edit-utilisateur-description-input').value;

        console.log("utilisateurName", utilisateurName);
        console.log("utilisateurDescription", utilisateurDescription);


        let utilisateur = new Utilisateur (utilisateurName, utilisateurDescription, elementId);
        elementId++;

        arrayUtilisateurs.next([...arrayUtilisateurs.getValue(), utilisateur]);
        console.log("Updated utilisateurs array:", arrayUtilisateurs.getValue());

        toggleFormPopup('add-piece-popup-form');
    });

    $arryUtilisateurs.subscribe({
        next: (response) => {
            console.log("arrayUtilisateur s Changed", arrayUtilisateurs.getValue());
            if (response.length > getHtmlTableLenght("utilisateur-list")) {
                console.log("utilisateurs", response);
                let row = document.createElement('tr');
                row.id = `${response[response.length - 1].description}`;
                let nameCell = document.createElement('td');
                let descriptionCell = document.createElement('td');
                let actionCell = document.createElement('td');
                let actionButtonRemove = document.createElement('button');
                actionButtonRemove.id = `remove-${response[response.length - 1].id}`;
                actionButtonRemove.textContent = "Remove";
                actionButtonRemove.onclick = function() {removeUtilisateur (response[response.length - 1].id);};

                // actionCell.appendChild(actionButtonRemove);
                actionCell.appendChild(actionButtonRemove);
                nameCell.textContent = response[response.length - 1].name;
                descriptionCell.textContent = response[response.length - 1].description;

                row.appendChild(nameCell);
                row.appendChild(descriptionCell);
                row.appendChild(actionCell);
                utilisateurTable.appendChild(row);
            }
              
        },
        error: (error) => {
            console.error(error);
        },
    });

    function removeUtilisateur (id) {
        console.log("removing utilisateur from array");
        const updatedUtilisateurs = arrayUtilisateurs.getValue().filter(utilisateur => utilisateur.id !== id);
        arrayUtilisateurs.next(updatedUtilisateurs);
         
        utilisateurTable.deleteRow(`utilisateur-${id}`);
        setTimeout(() => {}, 5000);
        console.log("current array:", arrayUtilisateurs.getValue());
    }
    
    function getHtmlTableLenght(tableId) {
        table = document.getElementById(tableId);
        return table.rows.length;
    }
});

function toggleFormPopup(overlay_id) {
    console.log("overlay_id form", overlay_id);
    const overlay = document.getElementById(overlay_id);
    console.log("overlay", overlay);
    overlay.classList.toggle('show');
    for (i = 0; i < document.getElementsByClassName('action-btn').length; i++) {
        document.getElementsByClassName('action-btn')[i].style.display =  document.getElementsByClassName('action-btn')[i].style.display === 'none' ? 'block' : 'none';
    }
}

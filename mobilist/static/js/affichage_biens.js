class Categorie {
    id;
    name;
    constructor(id, name){
        this.id = `cat-${id}`;
        this.name = name;
    }

    toString(){
        console.log(this.name);
        return this.name + " ";
    }
}



document.addEventListener("DOMContentLoaded", function() {
    const { BehaviorSubject } = rxjs; // import de rxjs apres avoir load le script dans le html car on utilise pas node et Typescript

    let elementId = 0;
    const arrayCategories = new BehaviorSubject([]);
    const $arryCategories = arrayCategories.asObservable();

    const catFormButton = document.getElementById('add-cat-btn');
    const catTable = document.getElementById('cat-list');

    catFormButton.addEventListener("click", function(event) {
        console.log("button clicked");

        event.preventDefault();
        let catName = document.getElementById('edit-cat-name-input').value;
    
        console.log("catName", catName);


        let cat = new Categorie(catName, elementId);
        elementId++;

        arrayCategories.next([...arrayCategories.getValue(), cat]);
        console.log("Updated rooms array:", arrayCategories.getValue());

        toggleFormPopup('add-cat-popup-form');
    });

    $arryCategories.subscribe({
        next: (response) => {
            console.log("arrayCategories Changed", arrayCategories.getValue());
            if (response.length > getHtmlTableLenght("cat-list")) {
                console.log("cat", response);
                let row = document.createElement('tr');
                row.id = `${response[response.length - 1].description}`;
                let nameCell = document.createElement('td');
                let descriptionCell = document.createElement('td');
                let actionCell = document.createElement('td');
                let actionButtonRemove = document.createElement('button');
                actionButtonRemove.id = `remove-${response[response.length - 1].id}`;
                actionButtonRemove.textContent = "Remove";
                actionButtonRemove.onclick = function() {removeRoom(response[response.length - 1].id);};

                actionCell.appendChild(actionButtonRemove);
                nameCell.textContent = response[response.length - 1].name;
                descriptionCell.textContent = response[response.length - 1].description;

                row.appendChild(nameCell);
                row.appendChild(descriptionCell);
                row.appendChild(actionCell);
                catTable.appendChild(row);
            }
              
        },
        error: (error) => {
            console.error(error);
        },
    });

    function removeRoom(id) {
        console.log("removing cat from array");
        const updatedCat = arrayCategories.getValue().filter(cat => cat.id !== id);
        arrayCategories.next(updatedCat);
         
        catTable.deleteRow(`cat-${id}`);
        setTimeout(() => {}, 5000);
        console.log("current array:", arrayCategories.getValue());
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

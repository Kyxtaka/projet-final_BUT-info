class Categorie {
    id;
    name;
    constructor(name, id){
        this.id = `cat-${id}`;
        this.name = name;
    }

    toString(){
        console.log(this.name);
        return this.name + " ";
    }
}

class TypeBien {
    id;
    name;
    constructor(name, id){
        this.id =`type-${id}`;
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
    const $arryCat = arrayCategories.asObservable();

    const catFormButton = document.getElementById('add-cat-btn');
    const catTable = document.getElementById('cat-list');

    catFormButton.addEventListener("click", function(event) {

        event.preventDefault();
        let catName = document.getElementById('edit-cat-name-input').value;

        let cat = new Categorie(catName, elementId);
        elementId++;

        arrayCategories.next([...arrayCategories.getValue(), cat]);
        console.log("Updated cat array:", arrayCategories.getValue());

        toggleFormPopup('add-cat-popup-form');
    });

    $arryCat.subscribe({
        next: (response) => {
            console.log("arrayCategories Changed", arrayCategories.getValue());
            if (response.length > getHtmlTableLenght("cat-list")) {
                console.log("cat", response);
                let row = document.createElement('tr');
                row.id = `${response[response.length - 1].description}`;
                let nameCell = document.createElement('td');
                let actionCell = document.createElement('td');
                let actionButtonRemove = document.createElement('button');
                actionButtonRemove.id = `remove-${response[response.length - 1].id}`;
                actionButtonRemove.textContent = "Remove";
                actionButtonRemove.onclick = function() {removeRoom(response[response.length - 1].id);};

                actionCell.appendChild(actionButtonRemove);
                nameCell.textContent = response[response.length - 1].name;
            
                row.appendChild(nameCell);
                row.appendChild(actionCell);
                catTable.appendChild(row);
            }
              
        },
        error: (error) => {
            console.error(error);
        },
    });

    function removeRoom(id) {
        const updatedCat = arrayCategories.getValue().filter(cat => cat.id !== id);
        arrayCategories.next(updatedCat);
         
        catTable.deleteRow(`room-${id}`);
        setTimeout(() => {}, 5000);
        }
    
    function getHtmlTableLenght(tableId) {
        table = document.getElementById(tableId);
        return table.rows.length;
    }

});

function toggleFormPopup(overlay_id) {
    const overlay = document.getElementById(overlay_id);
    overlay.classList.toggle('show');
    for (i = 0; i < document.getElementsByClassName('action-btn').length; i++) {
        document.getElementsByClassName('action-btn')[i].style.display =  document.getElementsByClassName('action-btn')[i].style.display === 'none' ? 'block' : 'none';
    }
}



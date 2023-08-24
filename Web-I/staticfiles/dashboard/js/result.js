function checkbox_checker(id) {
    if (document.getElementById(id).checked == false) {
        //Remove checkbox id
        form_val = document.getElementById('pass_form').value
        document.getElementById('pass_form').value = remove_val(form_val, id)
            // document.getElementById('fail_form').value = document.getElementById('pass_form').value

    } else {
        //Add checkbox id
        form_val = document.getElementById('pass_form').value
        document.getElementById('pass_form').value = add_val(form_val, id)
            // document.getElementById('fail_form').value = document.getElementById('pass_form').value
    }
}

function add_val(initial_val, val_to_add) {
    if (initial_val == "") {
        initial_val = val_to_add
        return initial_val
    }
    new_array = initial_val.split(",")
    new_array.push(val_to_add)
    new_array = new_array.sort()
    new_array.join(",")
    return new_array
}

function remove_val(initial_val, val_to_del) {
    if (initial_val == "") {
        return initial_val
    }
    new_array = initial_val.split(",")
    myindex = binary_searchh(new_array, val_to_del)
    if (myindex == -1) {
        return initial_val
    }
    new_array.splice(myindex, 1)
    new_array.join(",")
    return new_array
}

function binary_searchh(array, val) {
    start = 0;
    end = array.length;
    while (start <= end) {
        mid = Math.floor((start + end) / 2);
        if (array[mid] == val) {
            return mid;
        }
        if (array[mid] > val) {
            end = mid - 1;
        } else {
            start = mid + 1;
        }
    }
    return -1
}

function pass_me() {
    document.getElementById('pass_form').value = document.getElementById('pass_form').value + '**1'
}

function fail_me() {
    document.getElementById('pass_form').value = document.getElementById('pass_form').value + '**2'
}

function not_pass_me() {
    n = document.getElementById('pass_form').value.length
    document.getElementById('pass_form').value = document.getElementById('pass_form').value.substring(0, n - 3)
}

function not_fail_me() {
    n = document.getElementById('pass_form').value.length
    document.getElementById('pass_form').value = document.getElementById('pass_form').value.substring(0, n - 3)
}
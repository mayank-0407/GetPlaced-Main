$(document).ready(function() {
    var element = document.getElementById("main1");
    var positioninfo = element.getBoundingClientRect();
    var width = positioninfo.width;
    var element1 = document.getElementById("cr1");
    var positioninfo1 = element1.getBoundingClientRect();
    var width1 = positioninfo1.width;
    var req_w = (width - width1) * (0.45);
    var e = width1 - 40;
    $('#f1').css('width', e + 'px');
    $('.my_table').css('width', e + 'px');
    $('.my_table tr').css('width', e + 'px !important');
    $('.my_table tbody').css('width', e + 'px !important');
    // $('.input-field').css('width', e + 'px');
    var f2 = (e - 200) / 2;
    $('.profile_save_changes_btn').css('margin-left', f2 + 'px');
    $('.cards_form').css('margin-left', req_w + 'px');
    $('.cards_form').css('margin-right', req_w + 'px');
});
$(document).ready(function() {
    var element = document.getElementById("main1");
    var positioninfo = element.getBoundingClientRect();
    var width = positioninfo.width;
    var element1 = document.getElementById("cr1");
    var positioninfo1 = element1.getBoundingClientRect();
    var width1 = positioninfo1.width;
    var element2 = document.getElementById("profile_btn_2");
    var positioninfo2 = element2.getBoundingClientRect();
    var width2 = positioninfo1.width;
    var req_w = (width - width1) * (0.4);
    var e = width1 - 40;
    $('.comp_form').css('width', e + 'px');
    $('.comp_table').css('width', e + 'px');
    var f2 = (e - 200) / 2;
    var f3 = (e - 130) / 2;
    var f4 = (e - 100) * 0.45;
    // var f5 = (e-width2)*0.45;
    $('#div_img').css('margin-left', f4 + 'px');
    // $('.change_btn_2').css('margin-left', f5 + 'px');
    $('.profile_save_changes_btn').css('margin-left', f2 + 'px');
    $('.profile_save_changes_btn1').css('margin-left', f3 + 'px');
    $('.cards_form_comp').css('margin-left', req_w + 'px');
    $('.cards_form_comp').css('margin-right', req_w + 'px');
});
$(document).ready(function() {
    var element = document.getElementById("main1");
    var positioninfo = element.getBoundingClientRect();
    var width = positioninfo.width;
    var element1 = document.getElementById("cr11");
    var positioninfo1 = element1.getBoundingClientRect();
    var width1 = positioninfo1.width;
    // var element2 = document.getElementById("profile_btn_2");
    // var positioninfo2 = element2.getBoundingClientRect();
    // var width2 = positioninfo1.width;
    var req_w = (width - width1) * (0.4);
    var e = width1 - 40;
    $('.comp_form1').css('width', e + 'px');
    $('.comp_table1').css('width', e + 'px');
    var f2 = (e - 200) / 2;
    var f3 = (e - 130) / 2;
    var f4 = (e - 100) * 0.45;
    // var f5 = (e-width2)*0.45;
    // $('#div_img').css('margin-left', f4 + 'px');
    // $('.change_btn_2').css('margin-left', f5 + 'px');
    $('.profile_save_changes_btn4').css('margin-left', f2 + 'px');
    $('.profile_save_changes_btn3').css('margin-left', f3 + 'px');
    $('.cards_form_comp1').css('margin-left', req_w + 'px');
    $('.cards_form_comp1').css('margin-right', req_w + 'px');
});
$(document).ready(function() {
    $('.js-edit, .js-save').on('click', function() {
        var $form = $(this).closest('form');
        $form.toggleClass('is-readonly is-editing');
        var isReadonly = $form.hasClass('is-readonly');
        $form.find('input,textarea').prop('disabled', isReadonly);
        $form.find('select').prop('disabled', isReadonly);
        $form.find('input,file').prop('disabled', isReadonly);
    });
});
$(document).ready(function() {
    $('#div_img, #img_js_save').on('click', function() {
        var $form = $(this).closest('form');
        $form.toggleClass('is-readonly is-editing');
        var isReadonly = $form.hasClass('is-readonly');
        $form.find('input,file').prop('disabled', isReadonly);
    });
});

function validate_student_profile_3() {
    cgpa = document.getElementById("my_cgpa").value
    if (validate_cgpa(cgpa) == false) {
        alert("CGPA is not in proper format.")
        return false
    }
    return true
}

function validate_announcement_internship() {
    if (document.getElementById("duration").value.length <= 0) {
        alert("Internship Duration can not be empty.")
        return false
    }
    if (document.getElementById("number_of_students").value.length <= 0) {
        alert("Number of students can not be empty.")
        return false
    }
    if (document.getElementById("internship_position").value.length <= 0) {
        alert("Internship Position can not be empty.")
        return false
    }
    cgpa = document.getElementById("minimum_cgpa").value
    if (validate_cgpa(cgpa) == false) {
        alert("CGPA is not in proper format.")
        return false
    }
    stipend = document.getElementById("stipend").value
    if (validate_float(stipend) == false) {
        alert("Stipend is not in proper format.")
        return false
    }
    return true
}

function validate_company_profile_2() {
    if (document.getElementById("company_name").value.length <= 0) {
        alert("Company Name can not be empty.")
        return false
    }
    if (document.getElementById("address").value.length <= 0) {
        alert("Company Address can not be empty.")
        return false
    }
    return true
}

function validate_float(str) {
    if (str.match(/^(?=.+)(?:[1-9]\d*|0)?(?:\.\d+)?$/))
        return true;
    return false;

}

function validate_cgpa(str) {
    if (str.match(/^(10|\d)(\.\d{1,2})?$/))
        return true;
    return false;
}
// function validate_cgpa(str) {
//     if (validate_float(str)){
//       var fg=str.length();
//       if(parseInt(str)<10){
//         return true;
//       }
//       else if (parseFloat(str)==10) {
//         return true;
//       }
//     }
//     return false;
// }
$(document).ready(function() {
    $('#time_error1').fadeIn('slow', function() {
        $('#time_error1').delay(4000).fadeOut(4000);
    });
    $('#time_error2').fadeIn('slow', function() {
        $('#time_error2').delay(4000).fadeOut(4000);
    });
});

var inputBox = document.getElementById("inputBox");
var inputBox1 = document.getElementById("inputBox1");

var invalidChars = [
    "-",
    "+",
    "e",
];

inputBox.addEventListener("keydown", function(e) {
    if (invalidChars.includes(e.key)) {
        e.preventDefault();
    }
});
inputBox1.addEventListener("keydown", function(e) {
    if (invalidChars.includes(e.key)) {
        e.preventDefault();
    }
});


function validate_announcement(){
    round= document.getElementById("internship_round").value
    if(round<1){
        alert("Round must be greater than 0")
        return false
    }
    return true
}
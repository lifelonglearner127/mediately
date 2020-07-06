/* Project specific Javascript goes here. */
$(document).ready(function(){
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $('#myTable').DataTable({
        "ajax": "/tools/specs",
        "ordering": false,
        "columns": [
            {
                data: "name"
            },
            {
                data: "language"
            },
            {
                render: function(data, type, row) {
                    return `<button data-row_id="${row.id}" data-row_name="${row.name}" data-row_language="${row.language}" class="trigger-modal-btn">Edit</button>`
                }
            }
        ]
    });

    $("#create-tool").submit(function(){
        event.preventDefault();
        $(".submit-btn").attr("disabled", true)
        $.ajax({
            url: "/tools/specs/",
            dataType: "json",
            data: {
                name: $('#tool-name').val(),
                language: $('#tool-language').val()
            },
            type: "POST"
        })
        .done(function(data) {
            alert("Successully created, refresh the page")
            $(".submit-btn").removeAttr("disabled")
        })
        .fail(function(jqXHR, textStatus) {
            alert(jqXHR.responseText)
            $(".submit-btn").removeAttr("disabled")
        })
    });

    $(document).on('click', '.trigger-modal-btn', function() {
        $("#tool-id-2").val($(this).attr("data-row_id"))
        $("#tool-name-2").val($(this).attr("data-row_name"))
        $("#tool-language-2").val($(this).attr("data-row_language"))
        $("#exampleModal").modal('show')
    })
    $(".modal-submit-btn").click(function() {
        $(this).attr("disabled", true)
        var id = $('#tool-id-2').val()
        $.ajax({
            url: `/tools/specs/${id}/`,
            dataType: "json",
            data: {
                name: $('#tool-name-2').val(),
                language: $('#tool-language-2').val()
            },
            type: "PUT"
        })
        .done(function(data) {
            console.log(data)
            alert(data.msg)
            $(".modal-submit-btn").removeAttr("disabled")
            $("#exampleModal").modal('hide')
        })
        .fail(function(jqXHR, textStatus) {
            alert(jqXHR.responseText)
            $(".modal-submit-btn").removeAttr("disabled")
        })
    })
});

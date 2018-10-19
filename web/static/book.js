Status = {
  QUEUED : "queued",
  DOWNLOADING : "downloading",
  SUCCESS : "success",
  FAILED : "failed",
  RETRYING : "retrying",
  NOTEXIST : "not exist",
}


$('#frm_addbook').submit(function(event) { // catch the form's submit event
  $('#loading').show();
  $('#validate_result').text('Waiting to get book information...')
  var post_url = $(this).attr("action"); //get form action url

  // $("#listbook > tbody").prepend("<tr>" +
  //                                "<td>" + 'test1' + "</td>" +
  //                                "<td>" + 'test2' + "</td>" +
  //                                "<td>" + 'test3' + "</td>" +
  //                                "<td>" + 'test4' + "</td>" +
  //                                "<td>test5</td>" +
  //                                "<td>" + 'test6' + "</td>" +
  //                                "<td>" + 'test7' + "</td>" +
  //                                "</tr>");
  // return false;

  var form_data = {
    'bookid': $('#bookid').val(),
  }

  $.post(post_url, form_data).done(function(data){
    $('#loading').hide();
    console.log(JSON.stringify(data, undefined, 2));
    if (data['code'] != 0) {
      $('#validate_result').text(data['message']);
      $('#validate_result').css('color', 'red')
    } else {
      // validate success, add book to list
      $('#validate_result').text(data['title']);
      $('#validate_result').css('color', 'black')

      // add book to list
      addBookToList(data)
      //increment total book
      incrementTotalBook();
    }

  });

    event.preventDefault();
    return false; // cancel original event to prevent form submitting
});

function incrementTotalBook() {
  $('#totalbook').html(parseInt($('#totalbook').html(), 10)+1)

}


function addBookToList(data) {
  $("#tbl_listbook > tbody").prepend("<tr>" +
                                 "<td>" + data['addedDate'] + "</td>" +
                                 "<td>" + data['identifier'] + "</td>" +
                                 "<td>" + data['title'] + "</td>" +
                                 "<td>" + data['authorsName'] + "</td>" +
                                 "<td>" + data['issued'] + "</td>" +
                                 "<td><a target='_blank' href=" + data['web_url'] + ">" + data['web_url'] + "</a></td>" +
                                 "<td>" + data['downloadStatus'] + "</td>" +
                                 "<td>" + data['downloadPath'] + "</td>" +
                                 "<td>&nbsp;</td>" +
                                 "</tr>");
}

$('#redownload_book').click(function (event) {
    var answer = confirm("Do you want to redownload selected book");
    if (answer) {
      var post_url = "/redownload";
      var selected_book_ids = $("#tbl_listbook tr:has(td) input:checkbox:checked").map(function(){
        return $(this).val();
      }).get();

      console.log(selected_book_ids);

      if (selected_book_ids.length < 1) {
        alert("Please select book to redownload");
        return false;
      }

      var form_data = {'bookids': selected_book_ids};

      $.post(post_url, form_data).done(function (data) {
        console.log("redownload done", data);
        for(var bookid in data) {
            var book_status = data[bookid];
            updateStatus(bookid, book_status);

        }

      })

    }
    event.preventDefault();

});

function updateStatus(bookid, status) {
  if (status == Status.NOTEXIST) {
    // removed from db
    removeBook(bookid)
  } else {
      $('#tr_' + bookid).find('td[name="downloadStatus"]').html(status)
  }

}

$('#chkParent').click(function() {
  var isChecked = $(this).prop("checked");
  // $( "input[name='select_book']" ).prop('checked', isChecked);
  $('#tbl_listbook tr:has(td)').find('input[name="select_book"]').prop('checked', isChecked);
});


$('#delete_book').click(function (event) {
  var answer = confirm("Do you want to delete selected book");
  if (answer) {
    var post_url = "/delete";
    var selected_book_ids = $("#tbl_listbook tr:has(td) input:checkbox:checked").map(function(){
      return $(this).val();
    }).get();

    console.log(selected_book_ids);

    if (selected_book_ids.length < 1) {
      alert("Please select book to delete");
      return false;
    }

    var form_data = {'bookids': selected_book_ids};

    $.post(post_url, form_data).done(function (data) {
      console.log("delete done", data);
      for(var bookid in data) {
        removeBook(bookid);
      }

    })

  }
  event.preventDefault();

});

function removeBook(bookid) {
  $('#tr_' + bookid).remove();
}
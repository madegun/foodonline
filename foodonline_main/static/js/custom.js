let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      types: ["geocode", "establishment"],
      //default in this app is "IN" - add your country code
      componentRestrictions: { country: ["id"] },
    }
  );
  // function to specify what should happen when the prediction is clicked
  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  var place = autocomplete.getPlace();

  // User did not select the prediction. Reset the input field or alert()
  if (!place.geometry) {
    document.getElementById("id_address").placeholder = "Start typing...";
  } else {
    console.log("place name=>", place.name);
  }
  // get the address components and assign them to the fields
  var geocoder = new google.maps.Geocoder();
  var address = document.getElementById("id_address").value;

  geocoder.geocode({ address: address }, function (results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      var latitude = results[0].geometry.location.lat();
      var longitude = results[0].geometry.location.lng();

      $("#id_latitude").val(latitude);
      $("#id_longitude").val(longitude);

      $("#id_address").val(address);
      console.log(results);
    }
  });

  for (var i = 0; i < place.address_components.length; i++) {
    for (var j = 0; j < place.address_components[i].types.length; j++) {
      //get country name
      if (place.address_components[i].types[j] == "country") {
        $("#id_country").val(place.address_components[i].long_name);
      }
      //get state name
      if (
        place.address_components[i].types[j] == "administrative_area_level_1"
      ) {
        $("#id_state").val(place.address_components[i].long_name);
      }
      //get city name
      if (
        place.address_components[i].types[j] == "administrative_area_level_2"
      ) {
        $("#id_city").val(place.address_components[i].long_name);
      }
      //get pin_code name
      if (place.address_components[i].types[j] == "postal_code") {
        $("#id_pin_code").val(place.address_components[i].long_name);
      } else {
        $("#id_pin_code").val("");
      }
    }
  }
}

$(document).ready(function () {
  //ADD TO CART
  $(".add_to_cart").on("click", function (e) {
    e.preventDefault();

    food_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        //console.log(response)
        if (response.status == "login_required") {
          //console.log('raise the error message')
          swal(
            response.message,
            "silahkan login untuk melanjutkan belanja anda.",
            "info"
          ).then(function () {
            window.location = "/login";
          });
        } else if (response.status == "failed") {
          swal(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_counter"]);
          $("#qty-" + food_id).html(response.qty);

          //apply untuk function cartTotal
          cartTotal(
            response.cart_total['subtotal'],
            response.cart_total['tax'],
            response.cart_total['grand_total'],
          )
        }
      },
    });
  });

  //mengambil setiap qty on load even
  $(".item_qty").each(function () {
    var the_id = $(this).attr("id");
    var qty = $(this).attr("data-qty");

    $("#" + the_id).html(qty);
  });

  //DECREASE CART
  $(".decrease_cart").on("click", function (e) {
    e.preventDefault();

    food_id = $(this).attr("data-id");
    url = $(this).attr("data-url");
    cart_id = $(this).attr("id");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "login_require") {
          swal(
            response.message,
            "silahkan login untuk melanjutkan belanja anda.",
            "info"
          ).then(function () {
            window.location = "/login";
          });

        } else if (response.status == "failed") {
          swal(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_counter"]);
          $("#qty-" + food_id).html(response.qty);

          if(window.location.pathname == '/cart/'){
            removeCartItem(response.qty, cart_id);
            showCartEmpty();
          }

           //apply untuk function cartTotal
           cartTotal(
            response.cart_total['subtotal'],
            response.cart_total['tax'],
            response.cart_total['grand_total'],
          )
        }
      },
    });
  });

  $(".item_qty").each(function () {
    var the_id = $(this).attr("id");
    var qty = $(this).attr("data-qty");

    $("#" + the_id).html(qty);
  });

  //delete cart
  $(".delete_cart").on("click", function (e) {
    e.preventDefault();

    cart_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        console.log(response)
        if (response.status == "failed") {
          swal(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_counter"]);
          swal(response.status, response.message, 'info')

           //apply untuk function cartTotal
           cartTotal(
            response.cart_total['subtotal'],
            response.cart_total['tax'],
            response.cart_total['grand_total'],
          )

          removeCartItem(0, cart_id);
          showCartEmpty();
        }
      },
    });
  });


  //function untuk menghapus element cart list langsung ketika klik tombol delete
  function removeCartItem(cart_qty, cart_id){
    if(cart_qty <= 0 ){
      document.getElementById('cart-item-'+cart_id).remove();
    }
  }


  //function untuk menangani kalau cart kosong tampilkan display empty cart
  function showCartEmpty(){
    var checkCartIsEmpty = document.getElementById('cart_counter').innerHTML
    console.log(checkCartIsEmpty)
    if(checkCartIsEmpty == 0){
      document.getElementById("empty-cart").style.display = "block";

    }
  }

  // function untuk menangani cart total (subtotal, tax, gran_total)
  function cartTotal(subtotal, tax, grand_total){
    if(window.location.pathname == '/cart/'){
      $('#subtotal').html(subtotal);
      $('#tax').html(tax);
      $('#total').html(grand_total);
    }
  }

});

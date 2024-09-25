var src = {{jsonData|safe}}

function onSelectItem(item, element) {
  $('#output').html(
    '<p> School: <b>' + item.value.split(',')[0] + '</b> </p>' +
    ' <img src='+item.value.split(',')[1]+' > '
  );
}

$('#myAutocomplete').autocomplete({
  source: src,
  onSelectItem: onSelectItem,
  highlightClass: 'text-danger',
  threshold: 2,
});
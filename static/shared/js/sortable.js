var selected

function dragOver( e ) {
  if ( isBefore( selected, e.target ) ) e.target.parentNode.insertBefore( selected, e.target )
  else e.target.parentNode.insertBefore( selected, e.target.nextSibling )
}

function dragEnd() {
  selected = null
}

function dragStart( e ) {
  e.dataTransfer.effectAllowed = "move"
  e.dataTransfer.setData( "text/plain", null )
  selected = e.target
}

function isBefore( el1, el2 ) {
  var cur
  if ( el2.parentNode === el1.parentNode ) {
    for ( cur = el1.previousSibling; cur; cur = cur.previousSibling ) {
      if (cur === el2) return true
    }
  } else return false;
}
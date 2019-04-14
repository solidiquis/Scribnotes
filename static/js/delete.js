$(".delete_term").click(function(){
  return confirm("Are you sure you want to delete this item?\nAll courses and notes associated with this term will also be deleted.")
})
$(".delete_course").click(function(){
  return confirm("Are you sure you want to delete this item?\nAll notes associated with this term will also be deleted.")
})
$(".delete_note").click(function(){
  return confirm("Are you sure you want to delete this item?.")
})
$(".edit").click(function(){
  return confirm("Please create your document first.")
})

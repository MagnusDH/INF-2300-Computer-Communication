import React, {useState, useEffect, useRef} from "react";
import axios from "axios";

let id = 0;

//Main starting function
function Main ()
{
  const [ToDoList, setToDoList] = useState([])    //Create a list "ToDoList" and a function that modifies the "ToDoList". The list is initialized to empty "[]"
  const input = useRef()                          //Creating variable for fetching an input-string from user
  const [Get, setGet] = useState(0);
  const [Post, setPost] = useState(0);
  const [Delete, setDelete] = useState(-1);
  const [Put, setPut] = useState(-1);
  const [DeleteAll, setDeleteAll] = useState(-1);

  useEffect(() => 
  {

    // axios.get(`https://jsonplaceholder.typicode.com/todos/`).then(result => {
    axios.get(`http://localhost:5000/api/items/`).then(result => {
      const list = result.data;
      setToDoList(list);
    });
  }, [Get]);

  //Add
  useEffect(() =>
  {
    if(Post === 0) return;

    const inputString = input.current.value;

    if(inputString.length === 0) return;

    id += 1;

    axios.post(`http://localhost:5000/api/items/`, {done: false, id: id, name:inputString}).then(result => {
      setGet(Math.random());
      setPost(0);
      input.current.value = null;
    })
  }, [Post]);

  //Delete
  useEffect(() => 
  {
    if(Delete === -1) return;

    axios.delete(`http://localhost:5000/api/items/` + Delete).then(result => {
      setGet(Math.random());
      setDelete(-1)
    })
  }, [Delete])

  //Put
  useEffect(() => 
  {
    if(Put === -1) return;

    const find = ToDoList.items.filter(item => item.id === Put);
    let TrueOrFalse = undefined;

    if(find[0].done === true){
      TrueOrFalse = {done: true};
    }
    else{
      TrueOrFalse = {done: false};
    }

    axios.put(`http://localhost:5000/api/items/` + Put, {done: TrueOrFalse}).then(result => {
      setGet(Math.random());
      setPut(-1);
    })
  }, [Put])


  //DeleteAll
  useEffect(() => 
  {
    if(DeleteAll === -1) return;

    ToDoList.items.map(item => {
      return(
        axios.delete(`http://localhost:5000/api/items/` + item.id).then(result => {
          setGet(Math.random());
        })
      )
    })
    
    setDeleteAll(-1);

  }, [DeleteAll])

  //What is displayed on website
  return(
    <>                                                                {/*Function requires that only one element is returned, so wrap other elements in one element*/}
      <h1>"Online" To Do List</h1>                                      {/*Creating header*/}
      <input ref={input} type="text"/>                                {/*Fetching input from user*/}
      <button onClick={() => setPost(1)}>Add To Do</button>       
      <button onClick={() => {setDeleteAll(1)}}>Clear All To Dos</button>             

      <div>
        {ToDoList.items && ToDoList.items.map(item => {                                                       //Going through every variable in todoList and call each variable "item"
            return(
              <div key={item.id}>
                <input type="checkbox" onChange={() => setPut(item.id)}></input>   {/*Displaying how many todos left*/}
                {item.name}
                <button onClick={() => setDelete(item.id)}>Delete</button>
              </div>
            )
        })}
      </div>
    </> 
  )
}

export default Main;
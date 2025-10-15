import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common'
import { FormsModule } from '@angular/forms';
import { RouterLink } from "@angular/router";


import { NoteService } from '../../services/note.service';
import { NoteAddComponent } from '../../components/note-add/note-add.component';

@Component({
  selector: 'app-home',
  imports: [FormsModule, CommonModule, RouterLink, NoteAddComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  constructor(private noteService: NoteService) {}

  ngOnInit() {
    this.noteService.fetchNotes();
  }
  
  showAlert() {
    alert("Clicked!");
  }

  protected get notes() {
    return this.noteService.getNotes();
  }

}

import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common'

import { HeaderComponent } from "./header/header.component";
import { FooterComponent } from "./footer/footer.component";



@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    FormsModule,
    ReactiveFormsModule,
    CommonModule,
    HeaderComponent,
    FooterComponent
],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  

  title = 'soft-music';

  handleSubscribe() {
    console.log('Subscribed!');
    alert("Subscribed!");
  }
  
}

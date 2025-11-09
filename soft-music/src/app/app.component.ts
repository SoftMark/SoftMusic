import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common'

// Study
// import { HeaderComponent } from "./header/header.component";
// import { FooterComponent } from "./footer/footer.component";

import { HeaderComponent } from "./v1/compontents/header/header.component";



@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    FormsModule,
    ReactiveFormsModule,
    CommonModule,
    // HeaderComponent,
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

import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MyCalcComponent } from './my-calc/my-calc.component';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet, 
    FormsModule,
    ReactiveFormsModule,

    MyCalcComponent,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'soft-music';
}

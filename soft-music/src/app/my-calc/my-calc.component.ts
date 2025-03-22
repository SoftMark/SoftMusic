import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-my-calc',
  imports: [
    CommonModule,
    FormsModule,
  ],
  templateUrl: './my-calc.component.html',
  styleUrl: './my-calc.component.scss'
})
export class MyCalcComponent {
  public first: number = 1;
  public second: number = 1;

  public operation: string = '+';

  public operations: string[] = ['+', '-', '*'];

  public result?: number;
  
  public calc() {
    switch(this.operation) {
      case '+':
        this.result = this.first + this.second;
    }
  }
}
